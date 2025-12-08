from sqlalchemy.orm import Session
from typing import Optional
import asyncio
import json

from models.database import Translation, Chapter
from models.schemas import TranslationRequest, TranslationResponse


class TranslationService:
    def __init__(self):
        # In a real implementation, you would initialize a translation model or API client
        # For now, we'll simulate translation with basic mapping
        self.translation_cache = {}

    def get_cached_translation(self, content: str, target_lang: str) -> Optional[str]:
        """Check if translation is already cached"""
        cache_key = f"{content[:50]}-{target_lang}"  # Use first 50 chars as key
        return self.translation_cache.get(cache_key)

    def cache_translation(self, content: str, target_lang: str, translation: str):
        """Cache a translation"""
        cache_key = f"{content[:50]}-{target_lang}"
        self.translation_cache[cache_key] = translation

    def translate_text(self, text: str, target_lang: str = "ur", source_lang: str = "en") -> str:
        """Translate text to target language (simulated)"""
        # Check cache first
        cached = self.get_cached_translation(text, target_lang)
        if cached:
            return cached

        # In a real implementation, you would call a translation API like:
        # - Google Translate API
        # - Microsoft Translator API
        # - Hugging Face translation models
        # - OpenAI translation capabilities

        # For simulation purposes, return a placeholder translation
        # In a real implementation, you would have actual translation logic
        if target_lang == "ur":  # Urdu
            # This is a very basic simulation - in reality, you would use a proper translation API
            # Some common English to Urdu mappings for demonstration
            urdu_placeholders = {
                "robot": "روبوٹ",
                "ai": "مصنوعی ذہانت",
                "textbook": "کتاب",
                "chapter": "باب",
                "module": "ماڈیول",
                "artificial intelligence": "مصنوعی ذہانت",
                "robotics": "روبوٹکس",
                "embodied intelligence": "جسمانی ذہانت",
                "physical ai": "جسمانی مصنوعی ذہانت",
                "humanoid": "انسان نما",
                "nvidia": "این ویڈیا",
                "isaac": "آئزک",
                "ros": "آر او ایس",
                "gazebo": "گزیبو",
                "unity": "یونیٹی",
                "simulation": "شبیہ سازی",
                "vision": "دید",
                "language": "زبان",
                "action": "عمل",
                "learning": "سیکھنا",
                "perception": "ادراک",
                "planning": "منصوبہ بندی",
                "control": "کنٹرول",
                "navigation": "راہ نمائی",
                "manipulation": "ہاتھ سے کام لینا",
                "introduction": "تعارف",
                "overview": "جائزہ",
                "conclusion": "خاتمہ",
                "summary": "خلاصہ",
                "exercise": "مشق",
                "example": "مثال",
                "theory": "نظریہ",
                "practice": "عملی",
                "algorithm": "الگورتھم",
                "code": "کوڈ",
                "programming": "پروگرامنگ",
                "sensor": "سینسر",
                "actuator": "ایکچوایٹر",
                "controller": "کنٹرولر",
                "processor": "پروسیسر",
                "memory": "میموری",
                "data": "ڈیٹا",
                "information": "معلومات",
                "system": "سسٹم",
                "design": "ڈیزائن",
                "implementation": "عمل درآمد",
                "testing": "ٹیسٹنگ",
                "debugging": "ڈیبگنگ",
                "optimization": "آپٹیمائزر",
                "performance": "کارکردگی",
                "efficiency": "کفاءت",
                "accuracy": "درستگی",
                "reliability": "اعتماد",
                "safety": "حفاظت",
                "security": "سیکورٹی",
                "ethics": "اخلاقیات",
                "future": "مستقبل",
                "research": "تحقیق",
                "development": "ترقی",
                "innovation": "نوابدعت",
                "technology": "ٹیکنالوجی",
                "engineering": "انجنیرنگ",
                "computer": "کمپیوٹر",
                "software": "سافٹ ویئر",
                "hardware": "ہارڈ ویئر",
                "network": "نیٹ ورک",
                "internet": "انٹرنیٹ",
                "cloud": "کلاؤڈ",
                "database": "ڈیٹا بیس",
                "interface": "انٹرفیس",
                "user": "صارف",
                "experience": "تجربہ",
                "interaction": "تعامل",
                "feedback": "فیڈ بیک",
                "response": "جواب",
                "input": "ان پٹ",
                "output": "آؤٹ پٹ",
                "process": "عمل",
                "function": "فنکشن",
                "variable": "ویری ایبل",
                "loop": "لوپ",
                "condition": "شرط",
                "statement": "اسٹیٹمنٹ",
                "expression": "ایکسپریشن",
                "operator": "آپریٹر",
                "array": "ارے",
                "list": "لسٹ",
                "dictionary": "ڈکشنری",
                "object": "آبجیکٹ",
                "class": "کلاس",
                "method": "میتھڈ",
                "property": "پراپرٹی",
                "inheritance": "وراثت",
                "polymorphism": "پولی مارفزم",
                "encapsulation": "انکیپسولیشن",
                "abstraction": "اختصار",
                "problem": "مسئلہ",
                "solution": "حل",
                "approach": "طریقہ",
                "technique": "تکنیک",
                "methodology": "میتھڈالوجی",
                "framework": "فریم ورک",
                "library": "لائبریری",
                "package": "پیکج",
                "module": "ماڈیول",
                "component": "اجزا",
                "architecture": "فن تعمیر",
                "structure": "ساخت",
                "pattern": "پیٹرن",
                "template": "ٹیمپلیٹ",
                "configuration": "ترتیبات",
                "setting": "سیٹنگ",
                "parameter": "پیرامیٹر",
                "argument": "آرگومینٹ",
                "return": "واپسی",
                "exception": "استثناء",
                "error": "غلطی",
                "warning": "انتباہ",
                "debug": "ڈیبگ",
                "test": "ٹیسٹ",
                "unit": "یونٹ",
                "integration": "انضمام",
                "deployment": "تعیناتی",
                "maintenance": "بحالی",
                "documentation": "دستاویزات",
                "tutorial": "ٹیوٹوریل",
                "guide": "ہدایت نامہ",
                "reference": "حوالہ",
                "specification": "تفصیل",
                "requirement": "ضرورت",
                "constraint": "پابندی",
                "limitation": "حد",
                "advantage": "فائدہ",
                "disadvantage": "نقصان",
                "benefit": "فائدہ",
                "challenge": "چیلنج",
                "opportunity": "موقع",
                "risk": "رسک",
                "impact": "اثر",
                "analysis": "تحلیل",
                "evaluation": "تشخیص",
                "assessment": "جانچ",
                "measurement": "پیمائش",
                "metric": "میٹرک",
                "indicator": "اشارہ",
                "benchmark": "معیار",
                "standard": "معیار",
                "quality": "معیار",
                "assurance": "یقین",
                "validation": "تصدیق",
                "verification": "تصحیح",
                "certification": "تصدیق نامہ",
                "compliance": "رعایت",
                "governance": "انتظام",
                "management": "انتظام",
                "administration": "انتظام",
                "operation": "آپریشن",
                "execution": "عمل",
                "automation": "خودکاری",
                "intelligence": "ذہانت",
                "smart": "ذہین",
                "autonomous": "خود مختار",
                "adaptive": "موافق",
                "responsive": "جواب دہ",
                "interactive": "متبادل",
                "collaborative": "تعاونی",
                "distributed": "تقسیم شدہ",
                "scalable": "قابل توسیع",
                "flexible": "لچکدار",
                "robust": "مضبوط",
                "resilient": "مستحکم",
                "fault-tolerant": "غلطی برداشت",
                "high-availability": "اعلی دستیابی",
                "real-time": "حقیقی وقت",
                "parallel": "متوازی",
                "concurrent": "ہم وقت",
                "synchronous": "ہم وقت",
                "asynchronous": "غیر ہم وقت",
                "sequential": "ترتیبی",
                "random": "بے ترتیب",
                "stochastic": "تصادفی",
                "deterministic": "مقرر",
                "probabilistic": "احتمالی",
                "statistical": "شماریاتی",
                "mathematical": "ریاضی",
                "logical": "منطقی",
                "computational": "حسابی",
                "algorithmic": "الگورتھمی",
                "heuristic": "تجربی",
                "empirical": "تجربی",
                "theoretical": "نظری",
                "practical": "عملی",
                "experimental": "تجرباتی",
                "observational": "مشاهداتی",
                "descriptive": "وصفی",
                "prescriptive": "تعلیماتی",
                "predictive": "پیش گوئی",
                "diagnostic": "تشخیصی",
                "prescriptive": "تعلیماتی",
                "cognitive": "ادراکی",
                "perceptual": "ادراکی",
                "behavioral": "رویہ",
                "emotional": "جذباتی",
                "social": "اجتماعی",
                "ethical": "اخلاقی",
                "legal": "قانونی",
                "regulatory": "ریگولیٹری",
                "environmental": "ماحولیاتی",
                "economic": "اقتصادی",
                "financial": "مالی",
                "technical": "فنی",
                "scientific": "علمی",
                "academic": "تعلیمی",
                "educational": "تعلیمی",
                "instructional": "تعلیماتی",
                "pedagogical": "پیڈاگوجیکل",
                "curriculum": "نصاب",
                "syllabus": "سیلاバス",
                "lesson": "سبق",
                "lecture": "لیکچر",
                "workshop": "ورکشاپ",
                "seminar": "سمینار",
                "conference": "کانفرنس",
                "presentation": "پیش کش",
                "demonstration": "ڈیمو",
                "simulation": "شبیہ سازی",
                "visualization": "تصور",
                "animation": "حرکت",
                "graphics": "گرافکس",
                "multimedia": "ملٹی میڈیا",
                "virtual": "مجازی",
                "augmented": "اضافی",
                "mixed": "مخلوط",
                "extended": "توسیع شدہ",
                "immersive": "غمر شدہ",
                "interactive": "متبادل",
                "collaborative": "تعاونی",
                "social": "اجتماعی",
                "mobile": "موبائل",
                "wireless": "وائرلیس",
                "embedded": "اندراج شدہ",
                "real-time": "حقیقی وقت",
                "edge": "کنارہ",
                "fog": "دھند",
                "cloud": "کلاؤڈ",
                "hybrid": "مخلوط",
                "distributed": "تقسیم شدہ",
                "decentralized": "غیر مرکزی",
                "peer-to-peer": "ہم آہنگ",
                "client-server": "کلائنٹ-سرور",
                "microservices": "مائیکرو سروسز",
                "monolithic": "ایک جسمی",
                "service-oriented": "خدمت محور",
                "event-driven": "واقعہ محور",
                "data-driven": "ڈیٹا محور",
                "model-driven": "ماڈل محور",
                "api": "ای پی آئی",
                "rest": "ریسٹ",
                "graphql": "گراف کیو ال",
                "soap": "سویپ",
                "json": "جے ایس او این",
                "xml": "ایکس ایم ایل",
                "yaml": "یامل",
                "csv": "سی ایس وی",
                "database": "ڈیٹا بیس",
                "sql": "ایس کیو ایل",
                "nosql": "نو ایس کیو ایل",
                "relational": "تعلقی",
                "non-relational": "غیر تعلقی",
                "document": "دستاویز",
                "key-value": "کلید-قدر",
                "column-family": "کالم-خاندان",
                "graph": "گراف",
                "time-series": "وقت-سلسلہ",
                "spatial": "فضائی",
                "geographic": "جغرافیائی",
                "biometric": "بائیو میٹرک",
                "image": "تصویر",
                "video": "ویڈیو",
                "audio": "آڈیو",
                "text": "متن",
                "speech": "تقریر",
                "voice": "آواز",
                "sound": "آواز",
                "music": "موسیقی",
                "noise": "شور",
                "signal": "سگنل",
                "frequency": "فریکوئنسی",
                "amplitude": "اقدار",
                "phase": "مرحلہ",
                "waveform": "لہر شکل",
                "spectrum": "اسپیکٹرم",
                "filter": "فلٹر",
                "transform": "تبدیلی",
                "fourier": "فوریئر",
                "wavelet": "ویولیٹ",
                "convolution": "کنولوشن",
                "correlation": "تعلق",
                "regression": "رجیشن",
                "classification": "درجہ بندی",
                "clustering": "جمعیت",
                "dimensionality": "جہتیت",
                "reduction": "کمی",
                "feature": "خصوصیت",
                "extraction": "اخراج",
                "selection": "انتخاب",
                "engineering": "انجنیرنگ",
                "optimization": "آپٹیمائزر",
                "machine": "مشین",
                "deep": "گہرا",
                "neural": "نیورل",
                "network": "نیٹ ورک",
                "convolutional": "کنولوشنل",
                "recurrent": "بار بار",
                "generative": "پیداواری",
                "adversarial": "مخالف",
                "reinforcement": "تقویت",
                "unsupervised": "غیر نگران",
                "supervised": "نگران",
                "semi-supervised": "نصف نگران",
                "self-supervised": "خود نگران",
                "transfer": "منتقلی",
                "few-shot": "تھوڑے شاٹ",
                "zero-shot": "صفر شاٹ",
                "one-shot": "ایک شاٹ",
                "meta-learning": "میٹا لرننگ",
                "active": "فعال",
                "online": "آن لائن",
                "offline": "آف لائن",
                "batch": "بیچ",
                "incremental": "اضافی",
                "continual": "مسلسل",
                "lifelong": "زندگی بھر",
                "catastrophic": "تباہ کن",
                "forgetting": "بھولنا",
                "regularization": "ریگولرائزیشن",
                "normalization": "نارملائزیشن",
                "standardization": "معیاریت",
                "scaling": "سکیلنگ",
                "centering": "مرکزیت",
                "whitening": "سفید کرنا",
                "smoothing": "ہموار کرنا",
                "interpolation": "اندراج",
                "extrapolation": "خارجیت",
                "approximation": "تقریب",
                "estimation": "اندازہ",
                "prediction": "پیش گوئی",
                "forecasting": "پیش گوئی",
                "projection": "منصوبہ",
                "inference": "اندرونیت",
                "reasoning": "推理",
                "deduction": "کمی",
                "induction": "اضافی",
                "abduction": "اخراج",
                "logic": "منطق",
                "probability": "احتمال",
                "statistics": "شماریات",
                "calculus": "حسابان",
                "algebra": "جبر",
                "geometry": "ہندسہ",
                "trigonometry": "مثلثیات",
                "linear": "لکیری",
                "matrix": "میٹرکس",
                "vector": "ویکٹر",
                "tensor": "ٹینسر",
                "gradient": "ڈھال",
                "hessian": "ہیسین",
                "jacobian": "جیکوبین",
                "laplacian": "لاپلیسن",
                "divergence": "اختلاف",
                "curl": "گھماؤ",
                "integral": "انٹیگرل",
                "derivative": "مشتق",
                "partial": "جزوی",
                "ordinary": "عام",
                "stochastic": "تصادفی",
                "differential": "فرق",
                "equation": "مساوات",
                "inequality": "نامساوات",
                "optimization": "آپٹیمائزر",
                "constraint": "پابندی",
                "objective": "مقصد",
                "cost": "قیمت",
                "loss": "نقصان",
                "utility": "فائدہ",
                "reward": "انعام",
                "penalty": "سزا",
                "regularization": "ریگولرائزیشن",
                "sparsity": "کمی",
                "smoothness": "ہمواری",
                "convexity": "محدبیت",
                "concavity": "مقعریت",
                "monotonicity": "یکساں",
                "continuity": "مسلسلیت",
                "differentiability": "متعددیت",
                "integrability": "انٹیگریبلیٹی",
                "measurability": "پیمائش",
                "compactness": "کمپیکٹنس",
                "connectedness": "رابطہ",
                "path-connectedness": "راستہ رابطہ",
                "simple-connectedness": "سادہ رابطہ",
                "homotopy": "ہوموٹوپی",
                "homology": "ہومولوجی",
                "cohomology": "کوہومولوجی",
                "category": "زمرہ",
                "functor": "فنکٹر",
                "natural": "قدرتی",
                "transformation": "تبدیلی",
                "adjunction": "ملائیت",
                "limit": "حد",
                "colimit": "کولیمٹ",
                "product": "پراڈکٹ",
                "coproduct": "کوپراڈکٹ",
                "equalizer": "برابری",
                "coequalizer": "کوبرابری",
                "pullback": "پل بیک",
                "pushout": "پش آؤٹ",
                "terminal": "آخری",
                "initial": "ابتدائی",
                "zero": "صفر",
                "kernel": "کرنل",
                "cokernel": "کوکرنل",
                "image": "تصویر",
                "coimage": "کوتصویر",
                "subobject": "ذیلی آبجیکٹ",
                "quotient": "حصہ",
                "factor": "عامل",
                "composition": "ترکیب",
                "identity": "شناخت",
                "inverse": "الٹا",
                "automorphism": "خودروپی",
                "endomorphism": "اندروپی",
                "isomorphism": "سمروپی",
                "monomorphism": "ایکروپی",
                "epimorphism": "اپی روپی",
                "bimorphism": "دو روپی",
                "homeomorphism": "ہومیو روپی",
                "diffeomorphism": "ڈیفیو روپی",
                "homomorphism": "ہومو روپی",
                "morphism": "روپی",
                "group": "گروپ",
                "ring": "حلقہ",
                "field": "میدان",
                "module": "ماڈیول",
                "algebra": "الجبرا",
                "lattice": "جال",
                "poset": "پوزیٹ",
                "category": "زمرہ",
                "topos": "ٹوپوس",
                "sheaf": "شیف",
                "presheaf": "پری شیف",
                "scheme": "منصوبہ",
                "variety": "تنوع",
                "manifold": "منی فولڈ",
                "surface": "سطح",
                "curve": "منحنی",
                "line": "لائن",
                "plane": "سطح",
                "space": "فضا",
                "dimension": "جہت",
                "coordinate": "نقاط",
                "basis": "بنیاد",
                "frame": "فریم",
                "chart": "چارٹ",
                "atlas": "ایٹلس",
                "bundle": "بنڈل",
                "fiber": "فائب",
                "section": "سیکشن",
                "connection": "رابطہ",
                "curvature": "خمیدگی",
                "torsion": "ٹورشن",
                "holonomy": "ہولونومی",
                "parallel": "متوازی",
                "transport": "نقل و حمل",
                "geodesic": "جیوڈیسک",
                "metric": "میٹرک",
                "riemannian": "ریمانین",
                "symplectic": "سمپلیکٹک",
                "complex": "پیچیدہ",
                "kahler": "کاہلر",
                "hermitian": "ہرمتین",
                "euclidean": "یوکلڈین",
                "hyperbolic": "ہائپربولک",
                "elliptic": "ایلپٹک",
                "spherical": "کروی",
                "projective": "پروجیکٹیو",
                "affine": "افائن",
                "conformal": "کنفورمل",
                "isometric": "آئسو میٹرک",
                "isogonal": "آئسو گونل",
                "isotoxal": "آئسو ٹوکسل",
                "isohedral": "آئسو ہیڈرل",
                "polyhedron": "پولی ہیڈرون",
                "polytope": "پولی ٹوپ",
                "polygon": "پولی گون",
                "polyhedra": "پولی ہیڈرا",
                "polytopes": "پولی ٹوپس",
                "polygons": "پولی گونس",
                "tetrahedron": "ٹیٹرا ہیڈرون",
                "cube": "مکعب",
                "octahedron": "آکٹا ہیڈرون",
                "dodecahedron": "ڈوڈیکا ہیڈرون",
                "icosahedron": "آئیکوسا ہیڈرون",
                "sphere": "کروی",
                "torus": "ٹورس",
                "klein": "کلین",
                "bottle": "بوتل",
                "mobius": "موبیوس",
                "strip": "پٹی",
                "knot": "گانٹھ",
                "link": "ربط",
                "braid": "بالا",
                "fractal": "فریکٹل",
                "chaos": "بدتمیزی",
                "dynamical": "ڈائنامکل",
                "ergodic": "ارگوڈک",
                "stochastic": "تصادفی",
                "random": "بے ترتیب",
                "markov": "مارکوو",
                "process": "عمل",
                "brownian": "براؤنین",
                "motion": "حرکت",
                "wiener": "وینر",
                "ito": "ایٹو",
                "stratonovich": "سٹریٹونووچ",
                "levy": "لیوی",
                "poisson": "پوئسون",
                "gaussian": "گاؤسی",
                "normal": "نارمل",
                "uniform": "یونیفارم",
                "exponential": "ایکسپونینشل",
                "gamma": "گاما",
                "beta": "بیٹا",
                "chi-squared": "کائی سکویرڈ",
                "student": "سٹوڈنٹ",
                "fisher": "فشر",
                "binomial": "بائنومیل",
                "bernoulli": "برنولی",
                "geometric": "جغرافیائی",
                "negative": "منفی",
                "hypergeometric": "ہائپر جغرافیائی",
                "multinomial": "ملٹی نومیل",
                "dirichlet": "ڈیرچلیٹ",
                "wishart": "وشارت",
                "hotelling": "ہوٹلنگ",
                "wilks": "ولکس",
                "bartlett": "بارٹلیٹ",
                "box": "باکس",
                "anderson": "اینڈر سن",
                "darling": "ڈارلنگ",
                "kolmogorov": "کولموگوروو",
                "smirnov": "سمیرنوو",
                "cramer": "کریمر",
                "von": "ون",
                "mises": "میسیز",
                "watson": "واٹسن",
                "kuiper": "کوئپر",
                "anderson-darling": "اینڈر سن-ڈارلنگ",
                "cramer-von": "کریمر-ون",
                "mises-watson": "میسیز-واٹسن",
                "kuiper-anderson": "کوئپر-اینڈر سن"
            }

            translated_text = text.lower()
            for eng, urdu in urdu_placeholders.items():
                translated_text = translated_text.replace(eng, urdu)

            # If no specific translations matched, return a placeholder indicating it's translated
            if translated_text == text.lower():
                translated_text = f"[URDU TRANSLATION] {text} [TRANSLATION_END]"

        else:
            # For other languages, return a placeholder
            translated_text = f"[TRANSLATED TO {target_lang.upper()}] {text} [TRANSLATION_END]"

        # Cache the translation
        self.cache_translation(text, target_lang, translated_text)
        return translated_text

    def translate_chapter(self, db: Session, chapter_id: int, target_lang: str = "ur") -> str:
        """Translate an entire chapter"""
        # Get the chapter content
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter with id {chapter_id} not found")

        # Check if translation already exists in database
        existing_translation = db.query(Translation).filter(
            Translation.content_id == chapter_id,
            Translation.content_type == "chapter",
            Translation.language == target_lang
        ).first()

        if existing_translation:
            return existing_translation.translated_content

        # Translate the chapter content
        translated_content = self.translate_text(chapter.content, target_lang)

        # Save translation to database
        translation_record = Translation(
            content_id=chapter_id,
            content_type="chapter",
            language=target_lang,
            translated_content=translated_content
        )
        db.add(translation_record)
        db.commit()

        return translated_content

    def translate_content(self, db: Session, content: str, content_type: str, content_id: int, target_lang: str = "ur") -> str:
        """Translate any content (chapter, module, etc.)"""
        # Check if translation already exists in database
        existing_translation = db.query(Translation).filter(
            Translation.content_id == content_id,
            Translation.content_type == content_type,
            Translation.language == target_lang
        ).first()

        if existing_translation:
            return existing_translation.translated_content

        # Translate the content
        translated_content = self.translate_text(content, target_lang)

        # Save translation to database
        translation_record = Translation(
            content_id=content_id,
            content_type=content_type,
            language=target_lang,
            translated_content=translated_content
        )
        db.add(translation_record)
        db.commit()

        return translated_content

    def get_existing_translation(self, db: Session, content_id: int, content_type: str, target_lang: str) -> Optional[str]:
        """Get existing translation from database"""
        translation = db.query(Translation).filter(
            Translation.content_id == content_id,
            Translation.content_type == content_type,
            Translation.language == target_lang
        ).first()

        if translation:
            return translation.translated_content

        return None

    def batch_translate(self, texts: list, target_lang: str = "ur") -> list:
        """Translate multiple texts at once"""
        return [self.translate_text(text, target_lang) for text in texts]

    def translate_personalized_content(self, text: str, user_profile: dict, target_lang: str = "ur") -> str:
        """Translate content with personalization based on user profile"""
        # First translate the text
        translated_text = self.translate_text(text, target_lang)

        # Apply personalization based on user profile
        if user_profile.get("education_level") == "beginner":
            # Add simpler explanations for beginners
            translated_text = f"[مبتدی کے لیے آسان الفاظ میں] {translated_text}"
        elif user_profile.get("education_level") == "advanced":
            # Add more technical terms for advanced users
            translated_text = f"[ماہر کے لیے تکنیکی الفاظ میں] {translated_text}"

        # Add field-specific terminology
        field = user_profile.get("field_of_study", "").lower()
        if "robotics" in field:
            translated_text = f"[روبوٹکس کے تناظر میں] {translated_text}"
        elif "computer science" in field:
            translated_text = f"[کمپیوٹر سائنس کے تناظر میں] {translated_text}"
        elif "engineering" in field:
            translated_text = f"[انجنیرنگ کے تناظر میں] {translated_text}"

        return translated_text

    def translate_with_context(self, text: str, context: str, target_lang: str = "ur") -> str:
        """Translate text with context awareness"""
        # In a real implementation, context would influence translation choices
        # For now, we'll just append context information
        translated_text = self.translate_text(text, target_lang)
        return f"[سیاق و سباق: {context}] {translated_text}"


# Global instance of the translation service
translation_service = TranslationService()