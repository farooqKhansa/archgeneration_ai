import os
import tempfile
import time
import logging
from typing import Dict, Any
from fpdf import FPDF

logger = logging.getLogger("report_agent")

def clean_pdf_text(text: Any) -> str:
    """
    Cleans Unicode characters to avoid fpdf2 encoding errors on standard Latin-1 fonts.
    Replaces common characters with ASCII equivalents and drops unsupported ones.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    replacements = {
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u2013": "-",  # En dash
        "\u2014": "--", # Em dash
        "\u251c": "|--", # Box drawing ├
        "\u2514": "`--", # Box drawing └
        "\u2502": "|",   # Box drawing │
        "\u2500": "-",   # Box drawing ─
        "\u2022": "*",   # Bullet point
        "\u2192": "->",  # Arrow right
    }
    for unicode_char, ascii_replacement in replacements.items():
        text = text.replace(unicode_char, ascii_replacement)
        
    return text.encode("latin-1", errors="replace").decode("latin-1")

class ArchGenPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins: left, top, right
        self.set_margins(15, 15, 15)
        # Enable auto page break but handle height defensively
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "B", 8)
            self.set_text_color(100, 110, 120)
            self.cell(0, 5, "ARCHGEN AI - SYSTEM ARCHITECTURE REPORT", border=0, align="L")
            self.ln(5)
            # Draw a light grey line below the header
            self.set_draw_color(220, 225, 230)
            self.set_line_width(0.5)
            self.line(self.l_margin, self.t_margin + 6, 210 - self.r_margin, self.t_margin + 6)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        # Draw a thin line above the footer
        self.set_draw_color(220, 225, 230)
        self.set_line_width(0.5)
        self.line(self.l_margin, 297 - 15 - 2, 210 - self.r_margin, 297 - 15 - 2)
        self.cell(0, 10, f"Page {self.page_no()} of 7", border=0, align="C")

async def run_report_agent(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report Agent: Uses fpdf2 to generate a 7-page PDF report.
    Saves to the system temp directory as archgen_report.pdf
    """
    logger.info("Report Agent started execution.")
    start_time = time.perf_counter()
    
    # Ensure target folder exists
    pdf_dir = tempfile.gettempdir()
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "archgen_report.pdf")
    
    try:
        # Extract agent data from traces
        traces = pipeline_results.get("trace", [])
        
        req_data = {}
        arch_data = {}
        test_data = {}
        uml_data = {}
        db_data = {}
        boot_data = {}
        
        for trace in traces:
            agent = trace.get("agent")
            data = trace.get("data", {})
            if agent == "requirements_agent":
                req_data = data
            elif agent == "architecture_agent":
                arch_data = data
            elif agent == "testing_agent":
                test_data = data
            elif agent == "uml_agent":
                uml_data = data
            elif agent == "database_agent":
                db_data = data
            elif agent == "bootstrap_agent":
                boot_data = data

        # Initialize FPDF
        pdf = ArchGenPDF()
        
        # ----------------------------------------------------
        # PAGE 1: COVER PAGE
        # ----------------------------------------------------
        pdf.add_page()
        
        # Draw elegant dark blue banner
        pdf.set_fill_color(26, 36, 54) # Deep Navy
        pdf.rect(0, 0, 210, 85, 'F')
        
        # Title inside banner
        pdf.set_y(25)
        pdf.set_font("helvetica", "B", 26)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, "ARCHGEN AI", align="C")
        pdf.ln(12)
        
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "Software Requirements to Architecture Report", align="C")
        pdf.ln(10)
        
        pdf.set_y(95)
        pdf.set_text_color(30, 41, 59) # Slate 800
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Generated Artifact Suite", align="L")
        pdf.ln(10)
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(71, 85, 105) # Slate 600
        intro_text = (
            "This document compiles the automated analysis and designs produced by the ArchGen AI multi-agent "
            "engineering pipeline. This pipeline converts high-level requirements into actors, constraints, "
            "architectural patterns, test suites, UML layouts, SQL schema models, and project scaffolding specifications."
        )
        pdf.multi_cell(0, 6, clean_pdf_text(intro_text))
        
        pdf.ln(10)
        
        # Meta Box
        pdf.set_fill_color(248, 250, 252) # Slate 50
        pdf.set_draw_color(226, 232, 240) # Slate 200
        pdf.set_line_width(0.5)
        pdf.rect(15, 145, 180, 55, 'DF')
        
        pdf.set_y(150)
        pdf.set_x(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(50, 6, "Report Details")
        pdf.ln(6)
        
        pdf.set_x(20)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(50, 6, f"Generated At: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.ln(6)
        
        pdf.set_x(20)
        pdf.cell(50, 6, clean_pdf_text(f"Architecture Pattern: {arch_data.get('pattern', 'Layered Architecture')}"))
        pdf.ln(6)
        
        pdf.set_x(20)
        pdf.cell(50, 6, "Pipeline Status: SUCCESS")
        
        # ----------------------------------------------------
        # PAGE 2: REQUIREMENTS ANALYSIS
        # ----------------------------------------------------
        pdf.add_page()
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "1. Requirements Analysis")
        pdf.ln(10)
        
        # Actors
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "Target Actors & Personas")
        pdf.ln(8)
        pdf.set_font("helvetica", "", 10)
        for actor in req_data.get("actors", [])[:5]: # Cap to prevent overflow
            pdf.set_x(15)
            pdf.cell(5, 6, "-", align="C") # Safe standard bullet
            pdf.cell(175, 6, clean_pdf_text(f"  {actor}"))
            pdf.ln(6)
        pdf.ln(5)
        
        # Functional Requirements
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "Functional Requirements")
        pdf.ln(8)
        pdf.set_font("helvetica", "", 10)
        for req in req_data.get("functional_requirements", [])[:6]: # Cap to prevent overflow
            pdf.set_x(15)
            pdf.cell(5, 6, "-", align="C")
            pdf.multi_cell(175, 6, clean_pdf_text(f"  {req}"))
        pdf.ln(5)
        
        # Constraints
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "System Constraints")
        pdf.ln(8)
        pdf.set_font("helvetica", "", 10)
        for constraint in req_data.get("constraints", [])[:5]: # Cap to prevent overflow
            pdf.set_x(15)
            pdf.cell(5, 6, "-", align="C")
            pdf.multi_cell(175, 6, clean_pdf_text(f"  {constraint}"))

        # ----------------------------------------------------
        # PAGE 3: ARCHITECTURAL DESIGN
        # ----------------------------------------------------
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "2. Architectural Design & Pattern Selection")
        pdf.ln(10)
        
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, clean_pdf_text(f"Selected Pattern: {arch_data.get('pattern', 'Layered Architecture')}"))
        pdf.ln(8)
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "Architectural Reasoning & Trade-offs:")
        pdf.ln(6)
        pdf.set_font("helvetica", "", 10)
        reasoning = arch_data.get("reasoning", "No reasoning provided.")
        pdf.multi_cell(0, 6, clean_pdf_text(reasoning))
        pdf.ln(8)
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "Key System Components:")
        pdf.ln(6)
        pdf.set_font("helvetica", "", 10)
        for comp in arch_data.get("components", [])[:8]: # Cap to prevent overflow
            pdf.set_x(15)
            pdf.cell(5, 6, "-", align="C")
            pdf.multi_cell(175, 6, clean_pdf_text(f"  {comp}"))

        # ----------------------------------------------------
        # PAGE 4: TESTING PLAN
        # ----------------------------------------------------
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "3. Verification & Testing Suite")
        pdf.ln(10)
        
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 6, "The following test cases have been automatically mapped to requirements to ensure comprehensive verification coverage:")
        pdf.ln(5)
        
        test_cases = test_data.get("test_cases", [])[:4] # Cap to prevent overflow
        for tc in test_cases:
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, clean_pdf_text(f"Test Case {tc.get('id', 'N/A')}: {tc.get('requirement', 'N/A')}"))
            pdf.ln(6)
            
            pdf.set_font("helvetica", "I", 9)
            pdf.set_x(25)
            pdf.multi_cell(170, 5, clean_pdf_text(f"Description: {tc.get('description', '')}"))
            
            pdf.set_font("helvetica", "", 9)
            pdf.set_x(25)
            steps_str = " -> ".join(tc.get("steps", []))
            pdf.multi_cell(170, 5, clean_pdf_text(f"Steps: {steps_str}"))
            
            pdf.set_x(25)
            pdf.multi_cell(170, 5, clean_pdf_text(f"Expected Result: {tc.get('expected_result', '')}"))
            pdf.ln(4)

        # ----------------------------------------------------
        # PAGE 5: UML DIAGRAMS
        # ----------------------------------------------------
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "4. System UML Specifications (Mermaid)")
        pdf.ln(10)
        
        pdf.set_font("helvetica", "", 8)
        
        # Use Case Diagram
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "A. Use Case Diagram Code")
        pdf.ln(6)
        pdf.set_font("courier", "", 7.5)
        usecase_code = uml_data.get("use_case_diagram", "")
        pdf.multi_cell(0, 4, clean_pdf_text(usecase_code))
        pdf.ln(5)
        
        # Class Diagram
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "B. Class Diagram Code")
        pdf.ln(6)
        pdf.set_font("courier", "", 7.5)
        class_code = uml_data.get("class_diagram", "")
        pdf.multi_cell(0, 4, clean_pdf_text(class_code))
        pdf.ln(5)
        
        # Sequence Diagram
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "C. Sequence Diagram Code")
        pdf.ln(6)
        pdf.set_font("courier", "", 7.5)
        seq_code = uml_data.get("sequence_diagram", "")
        pdf.multi_cell(0, 4, clean_pdf_text(seq_code))

        # ----------------------------------------------------
        # PAGE 6: DATABASE SCHEMA
        # ----------------------------------------------------
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "5. Database Schema & ER Design")
        pdf.ln(10)
        
        # ER Diagram Code
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "A. Entity Relationship Diagram (erDiagram)")
        pdf.ln(6)
        pdf.set_font("courier", "", 8)
        er_code = db_data.get("er_diagram", "")
        pdf.multi_cell(0, 4, clean_pdf_text(er_code))
        pdf.ln(6)
        
        # SQL Schema Code
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "B. SQL Schema Definition (PostgreSQL)")
        pdf.ln(6)
        pdf.set_font("courier", "", 7.5)
        sql_code = db_data.get("sql_schema", "")
        pdf.multi_cell(0, 4, clean_pdf_text(sql_code))

        # ----------------------------------------------------
        # PAGE 7: PROJECT SCAFFOLDING & TASK BOARD
        # ----------------------------------------------------
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "6. Scaffolding Structure & Execution Board")
        pdf.ln(10)
        
        # Titles
        pdf.set_font("helvetica", "B", 10)
        pdf.set_x(15)
        pdf.cell(90, 6, "Scaffold Folder Structure")
        pdf.set_x(115)
        pdf.cell(80, 6, "Task Board Execution State")
        pdf.ln(6)
        
        # Print side-by-side using Y coordinates
        y_start = pdf.get_y()
        
        pdf.set_font("courier", "", 7.5)
        folder_str = boot_data.get("folder_structure", "")
        pdf.set_x(15)
        pdf.multi_cell(90, 3.5, clean_pdf_text(folder_str))
        y_folder_end = pdf.get_y()
        
        # Task Board
        pdf.set_y(y_start)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(115)
        pdf.cell(80, 5, "In Progress:")
        pdf.ln(5)
        
        pdf.set_font("helvetica", "", 8.5)
        for task in boot_data.get("task_board", {}).get("in_progress", []):
            pdf.set_x(115)
            pdf.multi_cell(80, 4.5, clean_pdf_text(f"- {task}"))
        
        pdf.set_x(115)
        pdf.ln(3)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(115)
        pdf.cell(80, 5, "Done:")
        pdf.ln(5)
        
        pdf.set_font("helvetica", "", 8.5)
        for task in boot_data.get("task_board", {}).get("done", []):
            pdf.set_x(115)
            pdf.multi_cell(80, 4.5, clean_pdf_text(f"- [x] {task}"))
            
        # Draw a little box with configuration file metadata at bottom
        pdf.set_y(max(y_folder_end, pdf.get_y()) + 10)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_x(15)
        pdf.cell(0, 6, "C. Configuration Files Generated")
        pdf.ln(6)
        
        pdf.set_font("helvetica", "", 9)
        config_files = boot_data.get("config_files", {})
        for name in config_files.keys():
            pdf.set_x(15)
            pdf.cell(5, 5, "-", align="C")
            pdf.cell(175, 5, clean_pdf_text(f"  {name} ({len(config_files[name].splitlines())} lines written)"))
            pdf.ln(5)

        # Output file
        pdf.output(pdf_path)
        
        logger.info(f"PDF successfully written to {pdf_path}. Total pages: {pdf.page_no()}")
        
    except Exception as e:
        logger.error(f"Report Agent error: {e}. Report generation failed.")
        return {
            "agent": "report_agent",
            "duration_ms": int((time.perf_counter() - start_time) * 1000),
            "data": {
                "pdf_path": "",
                "message": f"Report generation failed: {e}"
            }
        }

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"Report Agent completed execution in {duration_ms}ms.")
    
    return {
        "agent": "report_agent",
        "duration_ms": duration_ms,
        "data": {
            "pdf_path": pdf_path,
            "message": "Report generated successfully."
        }
    }
