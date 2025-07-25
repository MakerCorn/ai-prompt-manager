# General Rules

- Use best practices when generating code
- Use shared classes to avoid redundant code
- Use environment variables or command line parameters to set configuration options
- Always make output visually appealing
- Always update the readme after adding new functionality
- Always document your code and keep it organized
- Provide mermaid diagrams where appropriate in documents
- Implement 12-factor app principles whenever possible
- Always use the latest version of a library or API whenever possible.
- If you do not know an API, research the API. Do not create code based on a. non-existent API.
- Create unit test when needed to ensure reliability and error handling and place the files in a test folder
- When creating release pipelines, set it up to be triggered manually where the version is entered as the tag.
- Include in the changelog, all changes made in the current release. Use the standard versioning conventions.
- Keep all test files in the tests directory
- Keep all docs in the docs directory
- Always run mypy after code changes
- Always update the change log after making changes
- When changing base classes, always check dependencies for impacts of any refactoring of the interface.
- When fixing issuess after a refactoring, fix the caller not the implementor of the function first.
- Use the latest version of the `actions/upload-artifact` action. Version 3 has been deprecated, and we should use version 4.
- Do not add blank spaces at the end of lines when generating code.
- Avoid hard coding default values. Use variables or functions to configure or process values.
- Do not use Unicode characters (✅ emoji) in Windows CI environment. Use ASCII-only output.
- When generating code, run tests on the code to validate parameters and linting.
- When fixing code, analyze the root cause rather than just fixing the identified problem. For example, don't just fix parameters to match a parameter list, understand what the code was trying to do and fix the core problem.
- Remove deprecated classes and tests when refactoring code.
  