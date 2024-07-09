# cfn-error-detector

`cfn-error-detector` is a command-line tool that helps detect the root cause of AWS CloudFormation deployment failures. It can identify resources in error even within complex nested stacks, making troubleshooting easier and more efficient.

## Setup

### Install Rye

First, install Rye by following the [official installation guide](https://github.com/astral-sh/rye?tab=readme-ov-file#installation).

### Install cfn-error-detector

Once Rye is installed, you can install `cfn-error-detector` using the following command:

```sh
rye tools install --git 'https://github.com/ajisaka/cfn-error-detector' cfn-error-detector
```

This will install the `cfn-error-detector` command-line tool.

## Usage

If the stack name is `foo-app-stack`...

### Detect Error Cause

To show the cause of error for a specified stack, use the `detect` subcommand followed by the stack name. For example:

```sh
cfn-error-detector detect foo-app-stack
```

To display the path of the template file that caused the error, specify the root template file path.

```sh
cfn-error-detector detect foo-app-stack -t template.yaml
```

### Perform Stack Rollback

To manually initiate a stack rollback, use the `rollback` subcommand followed by the stack name:

```sh
cfn-error-detector rollback foo-app-stack
```

## Best Practices

### Disable Automatic Rollback

It's recommended to disable automatic rollback for CloudFormation stacks. When a stack rollback occurs, child stacks are deleted, which may cause failures in retrieving events (cloudformation:DescribeStackEvents). By disabling automatic rollback, you can better investigate the root cause of failures.

## Required AWS Permissions

To use `cfn-error-detector`, ensure your AWS IAM user or role has the following permissions:

- cloudformation:DescribeStackResources
- cloudformation:DescribeStacks
- cloudformation:DescribeStackEvents
- cloudformation:RollbackStack

## Contributing

Contributions to `cfn-error-detector` are welcome! Please refer to the project's GitHub repository for guidelines on how to contribute.

## Support

For issues, feature requests, or questions, please open an issue on the GitHub repository.
