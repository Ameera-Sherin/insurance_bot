class InsuranceRule:
    def __init__(self, insurance_type, coverage_limit, deductible, covered_procedures, exclusions=None, waiting_period=None):
        self.insurance_type = insurance_type
        self.coverage_limit = coverage_limit
        self.deductible = deductible
        self.covered_procedures = covered_procedures
        self.exclusions = exclusions if exclusions else []
        self.waiting_period = waiting_period

    def __repr__(self):
        return (f"{self.insurance_type} Rule: Coverage Limit=${self.coverage_limit}, "
                f"Deductible=${self.deductible}, Covered Procedures={self.covered_procedures}, "
                f"Exclusions={self.exclusions}, Waiting Period={self.waiting_period} days")


# Define sample insurance rules
insurance_rules = [
    InsuranceRule(
        insurance_type="Medical",
        coverage_limit=5000,
        deductible=500,
        covered_procedures="Yes",
        exclusions=["Cosmetic surgery", "Pre-existing conditions"],
        waiting_period=30
    ),
    InsuranceRule(
        insurance_type="Vehicle",
        coverage_limit=10000,
        deductible=1000,
        covered_procedures="Accidental damage, Theft",
        exclusions=["Wear and tear", "Intentional damage"],
        waiting_period=None
    ),
    InsuranceRule(
        insurance_type="Life",
        coverage_limit=20000,
        deductible=None,
        covered_procedures="Death by accident or natural causes",
        exclusions=["Suicide within 2 years", "Hazardous activities"],
        waiting_period=90
    ),
    InsuranceRule(
        insurance_type="Home",
        coverage_limit=8000,
        deductible=200,
        covered_procedures="Fire, Theft, Natural disasters",
        exclusions=["Floods", "Earthquakes"],
        waiting_period=60
    ),
    InsuranceRule(
        insurance_type="Travel",
        coverage_limit=3000,
        deductible=150,
        covered_procedures="Medical emergencies, Trip cancellations",
        exclusions=["Pre-existing medical conditions", "Travel to high-risk areas"],
        waiting_period=None
    )
]