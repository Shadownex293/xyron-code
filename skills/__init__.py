from .frontend import FRONTEND_SKILL
from .backend import BACKEND_SKILL
from .security import SECURITY_SKILL
from .refactor import REFACTOR_SKILL
from .preview import PREVIEW_SKILL
from .xsecurity import XSECURITY_SKILL
from .github import GITHUB_SKILL
from .xyron_test import XYRON_TEST_SKILL
from .xyron_docs import XYRON_DOCS_SKILL
from .xyron_translate import XYRON_TRANSLATE_SKILL
from .xyron_scraper import XYRON_SCRAPER_SKILL
from .xyron_convert import XYRON_CONVERT_SKILL

SKILL_REGISTRY = {
    "frontend":        FRONTEND_SKILL,
    "backend":         BACKEND_SKILL,
    "security":        SECURITY_SKILL,
    "refactor":        REFACTOR_SKILL,
    "preview":         PREVIEW_SKILL,
    "xsecurity":       XSECURITY_SKILL,
    "github":          GITHUB_SKILL,
    "xyron-test":      XYRON_TEST_SKILL,
    "xyron-docs":      XYRON_DOCS_SKILL,
    "xyron-translate": XYRON_TRANSLATE_SKILL,
    "xyron-scraper":   XYRON_SCRAPER_SKILL,
    "xyron-convert":   XYRON_CONVERT_SKILL,
}


def detect_skills(user_input: str) -> list:
    inp    = user_input.lower()
    result = []
    for name, skill in SKILL_REGISTRY.items():
        for trigger in skill["triggers"]:
            if trigger in inp:
                result.append(skill)
                break
    return result


def get_skill_prompt(skills: list) -> str:
    if not skills:
        return ""
    return "\n\n".join(s["prompt"] for s in skills)
