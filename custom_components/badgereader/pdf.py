import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_monthly_report(data, output_path):
    """
    Generates a simple PDF monthly report.

    Args:
        data (dict): A dictionary containing report data.
        output_path (str): The path to save the generated PDF.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add a title
    title = Paragraph("Monthly Badge Reader Report", styles['h1'])
    story.append(title)

    # Add some placeholder data
    story.append(Paragraph("Report Period: Placeholder Month Year", styles['Normal']))
    story.append(Paragraph("Total Hours Logged: XX.XX", styles['Normal']))
    story.append(Paragraph("Hours Balance at End of Month: +/- BB.BB", styles['Normal']))

    # Build the PDF
    doc.build(story)

if __name__ == '__main__':
    # Example usage
    report_data = {}  # Replace with actual data from Google Sheets
    output_directory = "reports"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_filename = os.path.join(output_directory, "monthly_report.pdf")

    generate_monthly_report(report_data, output_filename)
    print(f"Simple PDF report generated at: {output_filename}")