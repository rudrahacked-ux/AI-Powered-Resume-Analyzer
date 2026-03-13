import pandas as pd 
import numpy as np

np.random.seed(42)

num_samples = 2000

data = []

for _ in range(num_samples):

    cgpa = round(np.random.uniform(6, 10), 2)
    skills_count = np.random.randint(5, 30)
    projects = np.random.randint(0, 5)
    internships = np.random.randint(0, 3)
    ats_score = np.random.randint(40, 100)
    resume_score = np.random.randint(50, 100)

    # Realistic placement logic
    placement_probability = (
        0.3 * (cgpa / 10) +
        0.2 * (skills_count / 30) +
        0.15 * (projects / 5) +
        0.15 * (internships / 3) +
        0.1 * (ats_score / 100) +
        0.1 * (resume_score / 100)
    )

    placed = 1 if placement_probability > 0.6 else 0

    data.append([
        cgpa,
        skills_count,
        projects,
        internships,
        ats_score,
        resume_score,
        placed
    ])

df = pd.DataFrame(data, columns=[
    "cgpa",
    "skills_count",
    "projects",
    "internships",
    "ats_score",
    "resume_score",
    "placed"
])

df.to_csv("placement_dataset.csv", index=False)

print("✅ Synthetic dataset generated successfully!")
