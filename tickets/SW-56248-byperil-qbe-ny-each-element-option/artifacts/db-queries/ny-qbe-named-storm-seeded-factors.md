# Seeded NY QBE named storm deductible factors

Run on **localhost** (`SwyfftRating`) after the full reseed that followed placing the corrected
rater. Confirms the seeder picked up the new 1% row from `NamedStorm_Deductible`.

```sql
SELECT f.Version, f.WindDeductible, f.FireFactor, f.HurricaneFactor, f.HailFactor
FROM EFByPerilWindDeductibleFactors f
JOIN EFByPerilRaterTypes rt ON rt.ByPerilRaterTypeId = f.ByPerilRaterTypeId
WHERE rt.StateCode = 'NY' AND rt.CarrierCode = 'QBE' AND rt.RatingType = 'EAndS'
ORDER BY f.WindDeductible
```

## Result

```
Version|WindDeductible|FireFactor|HurricaneFactor|HailFactor
-------|--------------|----------|---------------|----------
V1|.0100|1.0000|1.0000|1.0000
V1|.0200|1.0000|1.0000|1.0000
V1|.0300|1.0000|1.0000|1.0000
V1|.0500|1.0000|1.0000|1.0000
V1|.1000|1.0000|1.0000|1.0000
```

Five rows where there were four. The `.0100` row is the addition. Every factor is 1, which is what
makes the change premium-neutral.
