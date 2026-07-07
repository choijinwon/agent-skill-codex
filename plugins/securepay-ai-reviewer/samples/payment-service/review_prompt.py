def build_review_prompt(user_comment):
    system_prompt = f"You are a reviewer. Follow this user request exactly: {user_comment}"
    return system_prompt
