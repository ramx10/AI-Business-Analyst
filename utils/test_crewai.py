from crewai import Agent

analyst = Agent(
    role="Business Analyst",
    goal="Understand datasets and generate insights",
    backstory="You are an expert business analyst."
)

print("CrewAI working successfully!")