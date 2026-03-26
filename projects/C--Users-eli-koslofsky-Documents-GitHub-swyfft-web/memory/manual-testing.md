# Manual Testing with Prompts

## How to Prompt the User for Manual QA Testing

When the plan says "prompt step-by-step for manual testing":

1. **Use the `AskUserQuestion` tool** — NOT plain text messages
2. **Provide SPECIFIC test data** — addresses, names, exact values to select. NEVER ask the user to find their own test data.
3. **One action per prompt** — don't dump all steps at once
4. **Give concrete options** — "Quote updated successfully" / "Got an error" / "Option not available"
5. **Keep prompts flowing** — immediately send the next prompt after getting a response, don't wait for confirmation

## Example Flow

- Prompt 1: "Navigate to beta.swyfft.com and start a quote for **123 Main St, Newark, NJ 07102**. Enter name Test User and click Get Quote. Are you on the quote page?"
- Prompt 2: "Under Additional Coverages, change Additional Replacement Cost to 25%. What happens?"
- Prompt 3: (next test step with specific data)

## Key Rules
- **ALWAYS provide test addresses** for each state being tested
- **ALWAYS provide exact field values** to enter/select
- **NEVER say "pick whichever is easier"** — give them the specific thing to test
- **NEVER use Playwright browser automation** when the plan says "manual test with prompts"
