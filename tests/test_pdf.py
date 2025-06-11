import pytest
from unittest.mock import patch, MagicMock

# Assuming the PDF generation function is named generate_monthly_report and takes data and a path as arguments
# Replace 'your_pdf_module' with the actual name of your pdf.py file
# Replace 'ReportLab' with the actual PDF library you are using
from custom_components.badgereader.pdf import generate_monthly_report


def test_generate_monthly_report():
    """
    Test the generate_monthly_report function.
    """
    mock_data = {
        "report_period": "May 2025",
        "start_balance": "+5.00 hrs",
        "total_logged": "40.00 hrs",
        "special_hours": "-2.00 hrs",
        "overall_actual": "38.00 hrs",
        "target_hours": "35.00 hrs",
        "variance": "+3.00 hrs",
        "end_balance": "+8.00 hrs",
        "detailed_log": [
            ["Date", "Check-in", "Check-out", "Duration", "Special", "Target", "Net", "Balance"],
            ["01/05/2025", "08:00", "16:00", "8.00", "0.00", "7.00", "1.00", "6.00"],
            ["02/05/2025", "08:00", "15:00", "7.00", "0.00", "7.00", "0.00", "6.00"],
        ]
    }
    mock_path = "/fake/report/path/monthly_report_may_2025.pdf"

    # Patch the PDF generation library's core objects/functions
    # Patch the reportlab components where they are defined and imported from
    with patch('custom_components.badgereader.pdf.SimpleDocTemplate') as MockSimpleDocTemplate, \
         patch('custom_components.badgereader.pdf.Paragraph') as MockParagraph, \
         patch('custom_components.badgereader.pdf.getSampleStyleSheet') as MockGetSampleStyleSheet, \
         patch('custom_components.badgereader.pdf.letter', (612.0, 792.0)) as mock_letter, \
         patch('builtins.open', new_callable=MagicMock) as mock_open:

        # Configure getSampleStyleSheet mock
        mock_styles = MagicMock()
        mock_styles.__getitem__.return_value = MagicMock() # So that styles['h1'], styles['Normal'] etc. work
        MockGetSampleStyleSheet.return_value = mock_styles

        # Mock the instance of SimpleDocTemplate and its build method
        mock_doc_instance = MagicMock()
        MockSimpleDocTemplate.return_value = mock_doc_instance

        # Configure mock_open to simulate a file
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        generate_monthly_report(mock_data, mock_path)

        # Verify that SimpleDocTemplate was instantiated
        MockSimpleDocTemplate.assert_called_once_with(mock_path, pagesize=(612.0, 792.0))

        # Verify that Paragraph was called (used for title and other data)
        MockParagraph.assert_called()

        # Verify getSampleStyleSheet was called
        MockGetSampleStyleSheet.assert_called_once()

        # Verify that the build method was called on the SimpleDocTemplate instance
        mock_doc_instance.build.assert_called_once()

        # builtins.open is patched to prevent actual file writes. We don't assert
        # its call when SimpleDocTemplate is fully mocked, as the mock's 'build'
        # method won't trigger the actual file saving sequence that calls 'open'.
        # The patch primarily serves as a safety net.
        # mock_open.assert_called_once_with(mock_path, "wb")