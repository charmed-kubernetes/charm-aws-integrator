import os
import pytest
import unittest.mock as mock

os.environ["JUJU_MODEL_UUID"] = TEST_MODEL_UUID = "test-model-uuid"
os.environ["JUJU_MACHINE_ID"] = TEST_MACHINE_ID = "0"
os.environ["JUJU_AVAILABILITY_ZONE"] = TEST_REGION = "us-east-1a"

# This must be imported after the environment variables are set
# to ensure they are available to the code being tested.
from lib.charms.layer import aws  # noqa: E402


def test_aws_iam_tag_invalid_calls():
    """Test the IAM tag function."""
    with pytest.raises(ValueError) as ie:
        aws._iam_tag("policy")
    assert (
        str(ie.value) == "Must specify either name or ARN for tagging resource='policy'"
    )

    with pytest.raises(ValueError) as ie:
        aws._iam_tag("policy", by_name="name", by_arn="arn")
    assert (
        str(ie.value)
        == "Cannot specify both name and ARN for tagging resource='policy'"
    )

    with pytest.raises(ValueError) as ie:
        aws._iam_tag("policy", by_name="name")
    assert (
        str(ie.value) == "Invalid resource type or missing name/arn: "
        "resource='policy' by_arn='' by_name='name'"
    )

    with pytest.raises(ValueError) as ie:
        aws._iam_tag("role", by_arn="arn")
    assert (
        str(ie.value) == "Invalid resource type or missing name/arn: "
        "resource='role' by_arn='arn' by_name=''"
    )


@mock.patch("lib.charms.layer.aws._aws")
def test_aws_iam_tag_policy(aws_mock):
    """Test the IAM tag function."""
    aws._iam_tag("policy", by_arn="charm.aws.s3-write")
    aws_mock.assert_not_called()
    aws._iam_tag(
        "policy", by_arn=f"arn:aws:iam::12345::charm.aws.{TEST_MODEL_UUID}.policy"
    )
    aws_mock.assert_called_once_with(
        "iam",
        "tag-policy",
        "--policy-arn",
        "arn:aws:iam::12345::charm.aws.test-model-uuid.policy",
        "--tags",
        f"Key=juju-model-uuid,Value={TEST_MODEL_UUID}",
    )


@mock.patch("lib.charms.layer.aws._aws")
def test_aws_iam_tag_role(aws_mock):
    """Test the IAM tag function."""
    aws._iam_tag("role", by_name=f"charm.aws.{TEST_MODEL_UUID}.role")
    aws_mock.assert_called_once_with(
        "iam",
        "tag-role",
        "--role-name",
        "charm.aws.test-model-uuid.role",
        "--tags",
        f"Key=juju-model-uuid,Value={TEST_MODEL_UUID}",
    )


@pytest.mark.parametrize(
    "message, expected_cls, expected_error_type",
    [
        # No recognisable error code → base AWSError with None type
        (
            "Something went wrong",
            aws.AWSError,
            None,
        ),
        # Standard AWS CLI prefix: "An error occurred (Code) when calling …"
        (
            "An error occurred (NoSuchEntity) when calling the GetRole operation: "
            "Role charm.aws.test-role not found.",
            aws.DoesNotExistAWSError,
            "NoSuchEntity",
        ),
        (
            "An error occurred (InvalidParameterValue) when calling the CreateRole "
            "operation: Invalid parameter.",
            aws.DoesNotExistAWSError,
            "InvalidParameterValue",
        ),
        (
            "An error occurred (DBInstanceNotFound) when describing instances "
            "operation: DB instance not found.",
            aws.DoesNotExistAWSError,
            "DBInstanceNotFound",
        ),
        (
            "An error occurred (EntityAlreadyExists) when calling the CreateRole "
            "operation: Role with name charm.aws.test-role already exists.",
            aws.AlreadyExistsAWSError,
            "EntityAlreadyExists",
        ),
        (
            "An error occurred (LimitExceeded) when calling the CreateRole operation: "
            "Limit exceeded.",
            aws.AlreadyExistsAWSError,
            "LimitExceeded",
        ),
        (
            "An error occurred (IncorrectState) when calling the DeleteDBInstance "
            "operation: Incorrect state.",
            aws.AlreadyExistsAWSError,
            "IncorrectState",
        ),
        # Unknown error code → base AWSError with the code preserved
        (
            "An error occurred (UnknownCode) when calling the SomeOperation operation.",
            aws.AWSError,
            "UnknownCode",
        ),
        # Error code NOT at the start of the string — re.search (not re.match) is needed
        (
            "aws: [ERROR]: An error occurred (EntityAlreadyExists) extra detail.",
            aws.AlreadyExistsAWSError,
            "EntityAlreadyExists",
        ),
        (
            "aws: [ERROR]: An error occurred (NoSuchEntity) extra detail.",
            aws.DoesNotExistAWSError,
            "NoSuchEntity",
        ),
    ],
)
def test_aws_error_get(message, expected_cls, expected_error_type):
    """Test AWSError.get factory with various message formats."""
    err = aws.AWSError.get(message)
    assert type(err) is expected_cls
    assert err.error_type == expected_error_type
    assert str(err) == message
