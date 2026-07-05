import logging
from typing import Dict, Optional
from pathlib import Path
import cv2

logger = logging.getLogger(__name__)


class DocumentOCRService:
    """Service for document OCR and text extraction"""

    def __init__(self, engine: str = "tesseract"):
        self.engine = engine
        self.ocr_model = None
        self._initialize_engine()

    def _initialize_engine(self):
        try:
            if self.engine == "tesseract":
                import pytesseract
                self.pytesseract = pytesseract
                logger.info(
                    "Tesseract OCR initialized"
                )

            elif self.engine == "easyocr":
                import easyocr
                self.ocr_model = easyocr.Reader(
                    ['en']
                )
                logger.info(
                    "EasyOCR initialized"
                )

            else:
                raise ValueError(
                    f"Unknown OCR engine: "
                    f"{self.engine}"
                )

        except Exception as e:
            logger.exception(str(e))
            raise

    @staticmethod
    def _preprocess_image(
        image_path: str
    ):
        """
        Preprocess image for OCR
        """
        image = cv2.imread(
            image_path
        )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0
        )

        _, thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY +
            cv2.THRESH_OTSU
        )

        return thresh

    def extract_text(
        self,
        image_path: str
    ) -> Dict:

        try:

            if not Path(
                image_path
            ).exists():
                raise FileNotFoundError(
                    f"Image not found: "
                    f"{image_path}"
                )

            if (
                self.engine ==
                "tesseract"
            ):
                return self._extract_tesseract(
                    image_path
                )

            return self._extract_easyocr(
                image_path
            )

        except Exception as e:

            logger.exception(
                str(e)
            )

            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0
            }

    def _extract_tesseract(
        self,
        image_path: str
    ) -> Dict:

        try:

            processed = (
                self
                ._preprocess_image(
                    image_path
                )
            )

            text = (
                self
                .pytesseract
                .image_to_string(
                    processed
                )
            )

            data = (
                self
                .pytesseract
                .image_to_data(
                    processed,
                    output_type='dict'
                )
            )

            confidences = []
            details = []

            for i in range(
                len(
                    data['text']
                )
            ):

                try:

                    conf = float(
                        data[
                            'conf'
                        ][i]
                    )

                    if conf > 0:

                        confidences.append(
                            conf
                        )

                        details.append({
                            "text":
                                data[
                                    'text'
                                ][i],

                            "confidence":
                                conf/100,

                            "bbox":
                                [
                                    data[
                                      'left'
                                    ][i],

                                    data[
                                      'top'
                                    ][i],

                                    data[
                                      'width'
                                    ][i],

                                    data[
                                      'height'
                                    ][i]
                                ]
                        })

                except:
                    pass

            avg = (
                sum(
                    confidences
                ) /
                len(
                    confidences
                )
                if confidences
                else 0
            )

            return {
                "success": True,
                "image_path":
                    image_path,
                "text":
                    text.strip(),
                "confidence":
                    avg/100,
                "quality":
                    self.assess_quality(
                        avg/100
                    ),
                "details":
                    details,
                "engine":
                    "tesseract"
            }

        except Exception as e:
            logger.exception(
                str(e)
            )
            raise

    def _extract_easyocr(
        self,
        image_path: str
    ) -> Dict:

        try:

            results = (
                self
                .ocr_model
                .readtext(
                    image_path
                )
            )

            texts = []
            confidences = []

            for (
                bbox,
                text,
                confidence
            ) in results:

                texts.append(
                    text
                )

                confidences.append(
                    confidence
                )

            avg = (
                sum(
                    confidences
                ) /
                len(
                    confidences
                )
                if confidences
                else 0
            )

            return {
                "success": True,
                "image_path":
                    image_path,
                "text":
                    " ".join(
                        texts
                    ),
                "confidence":
                    avg,
                "quality":
                    self.assess_quality(
                        avg
                    ),
                "details":
                    results,
                "engine":
                    "easyocr"
            }

        except Exception as e:
            logger.exception(
                str(e)
            )
            raise

    def extract_mrz(
        self,
        image_path: str
    ):

        try:

            from passporteye import (
                read_mrz
            )

            mrz = read_mrz(
                image_path
            )

            if not mrz:
                return None

            return mrz.to_dict()

        except:
            return None

    def extract_fields(
        self,
        image_path: str
    ) -> Dict:

        try:

            text_result = (
                self
                .extract_text(
                    image_path
                )
            )

            if not text_result[
                "success"
            ]:
                return text_result

            text = text_result[
                "text"
            ]

            fields = {

                "name":
                    self
                    ._extract_name(
                        text
                    ),

                "date_of_birth":
                    self
                    ._extract_date(
                        text
                    ),

                "document_number":
                    self
                    ._extract_document_number(
                        text
                    ),

                "expiry_date":
                    self
                    ._extract_expiry_date(
                        text
                    ),

                "nationality":
                    self
                    ._extract_nationality(
                        text
                    ),

                "document_type":
                    self
                    ._detect_document_type(
                        text
                    )
            }

            mrz = (
                self
                .extract_mrz(
                    image_path
                )
            )

            return {
                "success": True,
                "image_path":
                    image_path,
                "fields":
                    fields,
                "mrz":
                    mrz,
                "raw_text":
                    text,
                "confidence":
                    text_result[
                        "confidence"
                    ],
                "quality":
                    text_result[
                        "quality"
                    ]
            }

        except Exception as e:

            logger.exception(
                str(e)
            )

            return {
                "success": False,
                "error": str(e),
                "fields": {}
            }

    @staticmethod
    def assess_quality(
        confidence
    ):

        if confidence >= 0.90:
            return "excellent"

        if confidence >= 0.75:
            return "good"

        if confidence >= 0.50:
            return "fair"

        return "poor"

    @staticmethod
    def _detect_document_type(
        text: str
    ):

        text = text.upper()

        if "PASSPORT" in text:
            return "passport"

        if "DRIVING" in text:
            return "driving_license"

        if "IDENTITY" in text:
            return "national_id"

        return "unknown"

    @staticmethod
    def _extract_name(
        text: str
    ):

        lines = text.split(
            "\n"
        )

        for line in lines:

            words = (
                line
                .strip()
                .split()
            )

            if (
                len(words)
                >= 2
                and
                len(words)
                <= 4
            ):

                if all(
                    w.isalpha()
                    for w in words
                ):
                    return line.strip()

        return None

    @staticmethod
    def _extract_date(
        text: str
    ):

        import re

        matches = re.findall(
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            text
        )

        return (
            matches[0]
            if matches
            else None
        )

    @staticmethod
    def _extract_document_number(
        text: str
    ):

        import re

        matches = re.findall(
            r'[A-Z]{0,2}\d{6,9}',
            text
        )

        return (
            matches[0]
            if matches
            else None
        )

    @staticmethod
    def _extract_expiry_date(
        text: str
    ):

        import re

        matches = re.findall(
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            text
        )

        return (
            matches[-1]
            if matches
            else None
        )

    @staticmethod
    def _extract_nationality(
        text: str
    ):

        countries = [
            "USA",
            "UK",
            "CANADA",
            "INDIA",
            "AUSTRALIA",
            "FRANCE",
            "GERMANY"
        ]

        text = text.upper()

        for country in countries:
            if country in text:
                return country

        return None
