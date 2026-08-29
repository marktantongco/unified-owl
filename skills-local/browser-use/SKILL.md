# browser-use - Natural language browser automation

## Context
Use this skill whenever you need to browse the web, test a UI, scrape data, or perform any action that a real user would do in a browser — using natural language commands instead of raw Playwright scripts. This skill complements agent-browser (which provides CLI-based browser control) by offering a natural language interface. Use browser-use when the task is described in plain English; use agent-browser when you need precise CLI control.

## Instructions
1. Describe briefly the task (e.g., "Go to example.com, log in, click the dashboard link, and return the text of the first widget").
2. Invoke `browser-use` by prefixing your request with "Use browser to ...".
3. The skill will automatically launch a headful browser (or headless if configured) and execute your task.
4. It returns the result (HTML text, screenshots, or extracted data) without exposing the raw automation code.
5. If you need to do multi-step flows, you can chain commands: "Now click the 'settings' icon and tell me what appears."

## Constraints
- No manual Playwright code; always delegate to browser-use.
- Browser sessions are isolated — state is not shared between commands unless explicitly saved.
- Always assume a 10-second timeout for page loads; if a page is slow, wait but don't retry more than twice.
- Never enter real credentials in test scenarios; use environment variables for auth.

## Error Handling
All errors are typed and surfaced. Never swallow failures silently.

| Error Type | Code | When | Action |
|-----------|------|------|--------|
| `PageLoadTimeoutError` | BU-001 | Page doesn't load within 10s | Retry once, then report URL and timeout |
| `ElementNotFoundError` | BU-002 | Target element not in DOM | Report which selector/text was sought, suggest alternatives |
| `NavigationError` | BU-003 | Click or navigation doesn't reach expected URL | Screenshot current state, report expected vs actual URL |
| `AuthFailureError` | BU-004 | Login or auth step fails | Surface credentials issue, never retry with same creds |
| `SessionExpiredError` | BU-005 | Previous session state lost | Restart session, replay setup steps, notify user |
| `ScrapeEmptyError` | BU-006 | Extracted data is empty or malformed | Report what was expected vs what was found |

## Examples
1. "Use browser to open https://news.ycombinator.com and return the top 5 story titles."
2. "Use browser to log into our staging dashboard with email test@example.com, click on 'Reports', and tell me if the revenue chart is visible."
3. Error: "Use browser to click the 'Submit' button on form page" → button not found → raises `ElementNotFoundError(BU-002)` with message: "Element with text 'Submit' not found. Similar elements: 'Submit Form', 'Send'. Did you mean one of these?"
