"""
TCS Theme Taxonomy Definitions
21 predefined themes for hackathon idea classification
"""

THEME_TAXONOMY = {
    "AI & Machine Learning": {
        "description": "Artificial intelligence, machine learning models, neural networks, deep learning, NLP, computer vision",
        "keywords": ["AI", "ML", "neural network", "deep learning", "NLP", "computer vision", "LLM", "GPT", "transformer"]
    },
    "Cloud & Infrastructure": {
        "description": "Cloud computing, infrastructure as code, containerization, orchestration, serverless, DevOps",
        "keywords": ["cloud", "AWS", "Azure", "GCP", "Kubernetes", "Docker", "serverless", "infrastructure", "DevOps"]
    },
    "Data Analytics & Visualization": {
        "description": "Data analysis, business intelligence, dashboards, reporting, data visualization, insights",
        "keywords": ["analytics", "dashboard", "visualization", "BI", "reporting", "insights", "data analysis"]
    },
    "Cybersecurity": {
        "description": "Security solutions, threat detection, encryption, authentication, compliance, privacy",
        "keywords": ["security", "encryption", "authentication", "threat", "vulnerability", "compliance", "privacy"]
    },
    "Blockchain & Web3": {
        "description": "Blockchain technology, cryptocurrency, smart contracts, DeFi, NFTs, distributed ledger",
        "keywords": ["blockchain", "crypto", "smart contract", "DeFi", "NFT", "Web3", "distributed ledger"]
    },
    "IoT & Edge Computing": {
        "description": "Internet of Things, edge devices, sensors, embedded systems, real-time processing",
        "keywords": ["IoT", "edge", "sensor", "embedded", "device", "real-time", "telemetry"]
    },
    "Mobile Applications": {
        "description": "Mobile app development, iOS, Android, cross-platform, mobile UX, responsive design",
        "keywords": ["mobile", "iOS", "Android", "app", "React Native", "Flutter", "mobile UX"]
    },
    "Web Applications": {
        "description": "Web development, frontend, backend, full-stack, web frameworks, APIs",
        "keywords": ["web", "frontend", "backend", "API", "React", "Angular", "Vue", "Node.js", "Django"]
    },
    "Automation & RPA": {
        "description": "Process automation, robotic process automation, workflow automation, task automation",
        "keywords": ["automation", "RPA", "workflow", "bot", "automated", "process"]
    },
    "Sustainability & Green Tech": {
        "description": "Environmental solutions, carbon tracking, renewable energy, sustainability, climate tech",
        "keywords": ["sustainability", "green", "carbon", "renewable", "environment", "climate", "eco"]
    },
    "Healthcare & Wellness": {
        "description": "Health tech, telemedicine, patient care, medical devices, wellness apps, health monitoring",
        "keywords": ["health", "medical", "patient", "telemedicine", "wellness", "diagnosis", "healthcare"]
    },
    "Education & Learning": {
        "description": "EdTech, e-learning, training platforms, skill development, educational tools",
        "keywords": ["education", "learning", "training", "course", "student", "teacher", "EdTech"]
    },
    "Finance & FinTech": {
        "description": "Financial technology, payments, banking, investment, personal finance, trading",
        "keywords": ["finance", "payment", "banking", "investment", "trading", "FinTech", "wallet"]
    },
    "Supply Chain & Logistics": {
        "description": "Supply chain management, logistics optimization, inventory, tracking, warehouse management",
        "keywords": ["supply chain", "logistics", "inventory", "tracking", "warehouse", "shipping", "delivery"]
    },
    "Customer Experience": {
        "description": "CX improvement, customer service, chatbots, personalization, customer engagement",
        "keywords": ["customer", "CX", "chatbot", "personalization", "engagement", "service", "support"]
    },
    "HR & Workforce Management": {
        "description": "Human resources, recruitment, employee engagement, workforce planning, talent management",
        "keywords": ["HR", "recruitment", "employee", "workforce", "talent", "hiring", "onboarding"]
    },
    "Collaboration & Productivity": {
        "description": "Team collaboration, productivity tools, project management, communication platforms",
        "keywords": ["collaboration", "productivity", "team", "project management", "communication", "workspace"]
    },
    "Gaming & Entertainment": {
        "description": "Game development, entertainment platforms, AR/VR experiences, interactive media",
        "keywords": ["game", "gaming", "entertainment", "AR", "VR", "interactive", "metaverse"]
    },
    "Social Impact": {
        "description": "Social good, community development, accessibility, inclusion, humanitarian tech",
        "keywords": ["social", "community", "accessibility", "inclusion", "humanitarian", "impact", "nonprofit"]
    },
    "Smart Cities": {
        "description": "Urban technology, smart infrastructure, traffic management, public services, city planning",
        "keywords": ["smart city", "urban", "traffic", "public service", "infrastructure", "city", "municipal"]
    },
    "Other": {
        "description": "Ideas that don't fit into the above categories or span multiple domains",
        "keywords": []
    }
}


def get_theme_list() -> list:
    """Get list of all theme names"""
    return list(THEME_TAXONOMY.keys())


def get_theme_description(theme_name: str) -> str:
    """Get description for a specific theme"""
    return THEME_TAXONOMY.get(theme_name, {}).get('description', '')


def get_theme_keywords(theme_name: str) -> list:
    """Get keywords for a specific theme"""
    return THEME_TAXONOMY.get(theme_name, {}).get('keywords', [])
