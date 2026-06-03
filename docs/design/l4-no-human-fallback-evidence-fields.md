# L4 No-Human-Fallback Evidence Fields

Status: design note, v0.1

This design note adds a narrow L4 no-human-fallback review layer to ADSafetyPilot Scenario Evidence Packs. It is inspired by the ASIL E practitioner proposal, but it is not an ASIL E compliance claim and must not be presented as a published-standard requirement.

## Purpose

The current Scenario Evidence Pack chain is:

```text
Feature / scenario
  -> hazard or SOTIF triggering condition
  -> parameter distribution
  -> test case candidates
  -> evidence summary
```

For L4 systems, this is not enough. The evidence pack also needs to record whether the safety case credits a human fallback, whether the fallback is defensible within the fault-tolerance time interval, whether the policy layer covers the operational scenario space, and whether field monitoring feeds back into the safety case.

The added fields are:

- `no_human_controller`
- `fallback_credit`
- `policy_coverage_gap`
- `field_monitoring_evidence`

## Field 1: `no_human_controller`

Type: boolean

Meaning:

- `true`: the safety case does not credit an in-vehicle human driver or remote human controller for immediate control of the hazardous event.
- `false`: the safety case credits a human controller, or the scenario is not an L4 no-human-fallback case.

Usage:

- For L2 / L2+ evidence packs, this will usually be `false`.
- For L4 Robotaxi, L4 AVP, autonomous truck, unmanned shuttle, or low-speed unmanned delivery, this should be reviewed explicitly.

## Field 2: `fallback_credit`

Type: object

Suggested shape:

```yaml
fallback_credit:
  credited_actor: none
  claim: "No immediate human controller is credited for hazard avoidance."
  time_budget_ms: null
  evidence_status: not_yet_assessed
  evidence_required:
    - ftti_analysis
    - mrm_capability
    - remote_operation_latency
```

Allowed `credited_actor` values:

- `none`
- `in_vehicle_driver`
- `remote_operator`
- `remote_assistant`
- `field_staff`
- `infrastructure`
- `mixed`

Meaning:

This field makes any fallback assumption explicit. A remote operator can be recorded, but the evidence pack must then state whether the operator is credited as a real-time controller, a confirmer, a dispatcher, or a post-event responder.

## Field 3: `policy_coverage_gap`

Type: object

Suggested shape:

```yaml
policy_coverage_gap:
  status: partial
  open_policy_space:
    - emergency_vehicle_from_rear
    - temporary_traffic_control
  residual_rate_basis: field_monitoring_and_scenario_review
  evidence_required:
    - policy_coverage_matrix
    - scenario_enumeration
    - residual_rate_argument
```

Allowed `status` values:

- `not_applicable`
- `not_assessed`
- `partial`
- `bounded`
- `closed`

Meaning:

This field captures the risk that perception may be correct but the driving policy has no correct or validated response for the encountered scenario. For L4 systems, policy coverage should be treated as a first-class safety artifact, not just software correctness against a requirement.

## Field 4: `field_monitoring_evidence`

Type: object

Suggested shape:

```yaml
field_monitoring_evidence:
  required: true
  current_sources:
    - fleet_event_logs
    - remote_operation_records
    - ROAM_incident_taxonomy
  feedback_loop:
    - scenario_update
    - test_case_update
    - policy_update
    - safety_case_update
  evidence_status: not_yet_available
```

Meaning:

For L4, deployment evidence is part of the safety case. Field monitoring should show how real-world events update scenarios, test cases, policy rules, and the safety argument. ROAM can serve as the public incident and anomaly taxonomy layer; fleet logs and remote-operation records provide program-specific evidence.

## Example: L4 emergency vehicle interaction

```yaml
- id: CLAIM-L4-EV-NOFALLBACK-001
  claim_type: l4_no_human_fallback_review
  claim: "An L4 robotaxi emergency-vehicle interaction shall not credit an absent in-vehicle driver for hazard avoidance."
  no_human_controller: true
  fallback_credit:
    credited_actor: none
    claim: "No immediate human controller is credited for perception, policy selection, or maneuver execution."
    time_budget_ms: null
    evidence_status: not_yet_assessed
    evidence_required:
      - ftti_analysis
      - mrm_capability
      - remote_operation_boundary
  policy_coverage_gap:
    status: partial
    open_policy_space:
      - emergency_vehicle_from_rear
      - emergency_vehicle_in_intersection
      - multiple_emergency_vehicles
    residual_rate_basis: field_monitoring_and_scenario_review
    evidence_required:
      - policy_coverage_matrix
      - cross_modal_evidence_review
      - residual_rate_argument
  field_monitoring_evidence:
    required: true
    current_sources:
      - ROAM_incident_taxonomy
      - fleet_event_logs
      - remote_operation_records
    feedback_loop:
      - scenario_update
      - test_case_update
      - policy_update
      - safety_case_update
    evidence_status: required_for_l4_release
```

## Product interpretation

ADSafetyPilot should not expose this as “ASIL E compliance”. The customer-facing language should be:

- L4 no-human-fallback review
- No-human-controller evidence gap
- Field-monitoring-backed safety case
- Policy coverage analysis

The practical value is a sharper evidence gap report:

```text
This scenario has L4 no-human-fallback exposure.
Current evidence supports scenario parameterization and test case generation.
Missing evidence: fallback timing, policy coverage, and field monitoring loop.
```

