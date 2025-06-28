import requests

url = "https://convert-pptx-to-pdf-1034479052516.us-central1.run.app/convert"
data = {
    "bucket_name": "facthub-dev.firebasestorage.app",
    "input_gcs_pptx_file_path": "organizations/XjzlpcLWQzrKgsy2gtoN/createReportJobs/aa694938-8313-40b1-b460-6d102fd76c75/reportPlaceholderReplaceRequests/aa694938-8313-40b1-b460-6d102fd76c75/output/access_report.pptx",
    "output_gcs_pdf_file_path": "organizations/XjzlpcLWQzrKgsy2gtoN/createReportJobs/aa694938-8313-40b1-b460-6d102fd76c75/reportPlaceholderReplaceRequests/aa694938-8313-40b1-b460-6d102fd76c75/output/access_report.pdf"
}

response = requests.post(url, json=data)
print(response.json())
