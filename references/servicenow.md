# ServiceNow adaptation

Verify the instance release, application scope, actual table/field/variable names, existing controls and the team's transport method before design. Prefer platform configuration when it satisfies the requirement. Do not assume every change is a source-code diff.

Keep the team's existing work item, requirements and change records authoritative according to its declared ownership. Link exact application versions, approved update sets or other transport references as appropriate to the real setup.

For a request-validation pilot, inspect successful, empty, whitespace-only and alternative submission paths plus the nearest neighboring request item. Define expected access behavior rather than assuming a client-side check enforces a server-side invariant.

Run ATF only in development, test or other non-production instances. Evidence should name the tested version and environment. A checklist does not verify a platform control, and these skills do not supply ServiceNow credentials, connectors or deployment logic.

Source: https://www.servicenow.com/docs/r/application-development/automated-test-framework-atf/atf-landing-page.html
