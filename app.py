import streamlit as st
import os

st.set_page_config(page_title="NSE Daily Report Downloader", page_icon="📈")

st.title("🇰🇪 NSE Daily Market Reports")
st.write("This app provides easy access to the daily equity price lists collected from the Nairobi Securities Exchange.")

# The folder where GitHub Actions saves your PDFs
report_folder = "NSE_Daily_Reports"

if os.path.exists(report_folder):
    files = sorted(os.listdir(report_folder), reverse=True)
    
    if files:
        st.subheader("Available Reports")
        for file in files:
            file_path = os.path.join(report_folder, file)
            
            with open(file_path, "rb") as f:
                btn = st.download_button(
                    label=f"Download {file}",
                    data=f,
                    file_name=file,
                    mime="application/pdf"
                )
    else:
        st.info("No reports have been collected yet. The scraper runs at 3:15 PM EAT.")
else:
    st.error("Folder not found. Please run the scraper at least once.")

st.divider()
st.caption("Automated by GitHub Actions • Data source: NSE Kenya")
