# Simulation Sandbox

## Context

Activate this skill when the user needs to **test a scenario, decision, or piece of code** without real-world consequences. This includes:

- Evaluating architectural decisions before implementation
- Stress-testing business logic under hypothetical conditions
- Exploring "what-if" scenarios (market changes, load spikes, failure modes)
- Prototyping algorithms or data pipelines with synthetic data
- War-gaming strategic decisions (competitor moves, pricing changes)
- Testing code behavior with edge-case inputs

**Do not use** when the user needs real data analysis, wants to execute actual code in production, or requires factual reporting rather than speculative modeling.

## Instructions

### Step 1: Define the Simulation Scope
Before running any simulation, explicitly state:
- **What is being simulated** (system, process, decision, code)
- **Why it is being simulated** (question to answer, risk to evaluate)
- **Boundaries** (what is in scope and out of scope)
- **Key metrics** (what success/failure looks like)

### Step 2: Establish Parameters and Assumptions
List every parameter of the simulation:
- Input values (and their source: real data, synthetic, or estimated)
- Environmental conditions (load, time period, external factors)
- Assumptions that simplify the model (and their potential impact)
- Fixed variables vs. variables to be tested across ranges

### Step 3: Build the Simulation Model
Construct the simulation step by step:
- Describe the initial state
- Define the rules/logic that govern each step
- Identify feedback loops or cascading effects
- Set the number of iterations or time steps

### Step 4: Run Scenarios
Execute the simulation across multiple scenarios:
- **Baseline scenario:** Expected/normal conditions
- **Best case:** Optimistic but plausible inputs
- **Worst case:** Pessimistic but plausible inputs
- **Edge cases:** Boundary conditions, extreme values, zero-input states
- **Stress test:** Push parameters beyond normal operating range

### Step 5: Observe and Record Outcomes
For each scenario, capture:
- Key metric values at each time step or iteration
- Points of failure, divergence, or unexpected behavior
- Patterns that emerge across multiple scenarios
- Differences between scenarios that reveal sensitivities

### Step 6: Report Findings
Present results with clear structure:
- Executive summary (2-3 sentences)
- Scenario comparison table
- Key findings and patterns
- Sensitivity analysis (which inputs had the largest effect)
- Limitations of the simulation
- Recommended next steps

### Step 7: Label Everything
Every piece of output must be clearly labeled:
- All numbers are prefaced with `[SIMULATED]`
- All results are framed as "In this simulation model..." or "Under these parameters..."
- Never present simulated data as empirical fact

## Constraints

1. **Always label simulated outputs.** Use `[SIMULATED]` tags prominently. Failure to do so is a critical violation.
2. **State limitations explicitly.** Every simulation has blind spots — name them.
3. **Use plausible parameters.** Even stress tests should use values that could theoretically occur. Purely fantastical inputs waste the user's time.
4. **Never claim predictive accuracy.** Simulations explore possibilities; they do not predict the future. Use language like "suggests," "indicates," "under these conditions."
5. **Separate signal from noise.** If a result is driven by a simplifying assumption rather than genuine dynamics, call that out.
6. **Complete the full cycle.** Every simulation must include Steps 1-7. Do not skip reporting or labeling.
7. **No real data without explicit permission.** If the user provides real data, note that it is real data and keep it separate from synthetic/simulated elements.

## Examples

### Example 1: API Load Testing Simulation

**User:** "We're expecting 10x traffic next month. Will our API survive?"

**Output:**

```
=== SIMULATION: API Load Capacity Test ===

Step 1 - Scope
  System: REST API (Node.js/Express, PostgreSQL, Redis cache)
  Question: At what traffic multiplier does the API begin to degrade?
  Key metrics: P50 latency, P99 latency, error rate (%)

Step 2 - Parameters
  - Current baseline: 500 req/sec, P50=45ms, P99=120ms, error rate=0.1%
  - DB pool size: 20 connections (max)
  - Redis cache hit rate: 85% (assumed constant)
  - Worker threads: 4 (assumed)
  [ASSUMPTION] Infrastructure scales vertically, not horizontally

Step 3 - Model
  Each simulation step = 1 second of sustained traffic.
  Logic: req/sec -> connection pool utilization -> queue depth -> latency.
  Failure trigger: queue depth > 100 or error rate > 5%.

Step 4 - Scenarios Run
  | Scenario     | req/sec  | P50 (ms) | P99 (ms)   | Error Rate   |
  |--------------|----------|----------|------------|--------------|
  | Baseline     | [SIM] 500| [SIM] 45 | [SIM] 120  | [SIM] 0.1%   |
  | 3x load      | [SIM]1500| [SIM] 62 | [SIM] 210  | [SIM] 0.3%   |
  | 5x load      | [SIM]2500| [SIM] 98 | [SIM] 450  | [SIM] 1.2%   |
  | 10x load     | [SIM]5000| [SIM]340 | [SIM] 2100 | [SIM] 8.7%   |

Step 5 - Key Findings
  [SIMULATED] Degradation begins between 3x-5x load. At 10x, the system
  is beyond acceptable thresholds. Connection pool saturation is the
  primary bottleneck — not CPU or memory.

Step 6 - Limitations
  - [SIMULATED] Cache hit rate assumed constant; in reality it may degrade
  - No network latency or CDN effects modeled
  - Database query complexity assumed uniform

Recommendation: Under these [SIMULATED] conditions, horizontal scaling
of the API layer + connection pooling optimization should begin before 5x load.
```

### Example 2: Pricing Strategy Simulation

**User:** "Should we lower our SaaS price from $99 to $69 to win more customers?"

**Output:**

```
=== SIMULATION: Pricing Strategy Impact ===

Step 1 - Scope
  Decision: Reduce monthly price from $99 to $69.
  Question: Does the volume gain compensate for revenue per-user loss?
  Key metrics: MRR, customer count, churn rate, break-even conversion lift.

Step 2 - Parameters
  - Current: 2,000 customers, $99/mo, 3% monthly churn
  - Price elasticity assumption: 1.4 (14% volume gain per 10% price drop)
  - [ASSUMPTION] churn rate unchanged at new price point

Step 3 - Model
  Simulated over 12 months. Each month: new conversions -> churned users ->
  net customer count -> MRR. Conversion rate scales with price elasticity.

Step 4 - Key Results
  [SIMULATED] Break-even conversion lift required: 43.5% more customers

  | Month     | Customers | [SIM] MRR    | vs. Current |
  |-----------|-----------|--------------|-------------|
  | Month 0   | 2,000     | $198,000     | baseline    |
  | Month 3   | 2,520     | [SIM] $173,880 | -12.2%    |
  | Month 6   | 2,870     | [SIM] $198,030 | ~breakeven |
  | Month 12  | 3,340     | [SIM] $230,460 | +16.4%    |

Step 5 - Limitations
  [SIMULATED] Churn assumed constant — lower price may attract
  higher-churn customers. Competitor response not modeled.

Recommendation: Under [SIMULATED] conditions, the price cut breaks even
around month 6 and generates +16% MRR by month 12 — but ONLY if churn
holds steady. Test with a cohort first before full rollout.
```
