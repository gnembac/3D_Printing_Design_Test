# Supplier RFQ Template

> Binding technical language is English. Use short, unambiguous sentences,
> SI units (mm, g, kg, N, MPa, °C) and `.` as decimal separator. See
> `docs/reference/project-specification-de.md` §13 for the full supplier
> rulebook (DFM, change control, Golden Sample, AQL, IP protection).

```text
Please quote according to the attached manufacturing package only.

Part Number:
Revision:
Process:
Material:
Color:
Quantity:
Required delivery date:
Destination country:

Please confirm the following in your quotation:

1. Manufacturing process and machine class.
2. Exact material manufacturer and grade.
3. Ability to meet all CTQ dimensions and tolerances.
4. Proposed print orientation.
5. Proposed support locations and post-processing.
6. Material lead time and production lead time.
7. Inspection method for every CTQ feature.
8. Whether subcontracting is required.
9. Whether any requirement is not achievable.
10. Confirmation that no material or process substitution will be made
    without written approval.

Please return:
- quotation,
- DFM feedback,
- material datasheet,
- sample inspection report,
- lead time,
- packaging proposal,
- deviation list, if applicable.
```

**Binding response rule:** if the supplier does not explicitly confirm a
requirement, the requirement is considered not accepted.

No RFQ is sent to a supplier without explicit user approval
(see CLAUDE.md "Safety and scope").
