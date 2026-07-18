from pathlib import Path
from fastapi.testclient import TestClient

import pytest
from backend.main import app
from backend.config.settings import settings

client = TestClient(app)

@pytest.mark.skipif(
    settings.MISTRAL_API_KEY.get_secret_value() == "dummy-key-for-tests",
    reason="Skipping E2E test in CI because a real Mistral API key is required"
)
def test_end_to_end_workflow():
    """
    End-to-End Workflow Test:
    CSV Upload -> Auditor -> Planner -> Analytics -> Insights -> 
    Validation -> Visualization -> Report -> Dashboard -> ZIP
    """
    dataset_name = "finsight_sample_sales_dataset.csv"
    
    # Ensure the sample dataset exists at root
    sample_path = Path(dataset_name)
    assert sample_path.exists(), f"Missing {dataset_name} in root directory."
    
    print(f"\n--- Starting E2E Test on {dataset_name} ---")
    
    # 1. Upload CSV
    print("[1/5] Uploading CSV...")
    with open(sample_path, "rb") as f:
        upload_response = client.post(
            f"{settings.API_V1_STR}/upload",
            files={"file": (dataset_name, f, "text/csv")}
        )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert upload_data["dataset_name"] == dataset_name
    
    # 2. Trigger Analysis (TestClient runs background tasks synchronously)
    print("[2/5] Triggering Analysis (this will run the entire LangGraph workflow)...")
    analyze_response = client.post(
        f"{settings.API_V1_STR}/analyze",
        json={"filename": dataset_name}
    )
    assert analyze_response.status_code == 200
    analyze_data = analyze_response.json()
    workflow_id = analyze_data["workflow_id"]
    assert workflow_id is not None
    
    # 3. Check Workflow Status
    print(f"[3/5] Verifying Workflow Status for {workflow_id}...")
    status_response = client.get(f"{settings.API_V1_STR}/workflow/{workflow_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "COMPLETED"
    
    # 4. Verify Final Artifacts Paths from /reports endpoint
    print("[4/5] Checking generated artifact APIs...")
    reports_response = client.get(f"{settings.API_V1_STR}/reports/{workflow_id}")
    assert reports_response.status_code == 200
    reports_data = reports_response.json()
    
    assert "generated_files" in reports_data
    assert len(reports_data["generated_files"]) > 0
    
    # 5. Verify physical files were actually created in the exports directory
    print("[5/5] Verifying physical files on disk...")
    exports_dir = Path(settings.EXPORTS_DIR)
    workflow_dir = exports_dir / "workflows" / workflow_id
    packages_dir = exports_dir / "packages"
    
    assert workflow_dir.exists(), "Workflow directory was not created."
    assert (workflow_dir / "dashboard" / "Dashboard.html").exists(), "Dashboard.html not found."
    assert (workflow_dir / "dashboard" / "Trace.html").exists(), "Trace.html not found."
    assert list((workflow_dir / "reports").glob("*.pdf")), "PDF report not found."
    assert (workflow_dir / "logs" / "agent_trace.json").exists(), "agent_trace.json not found."
    assert (workflow_dir / "analytics" / "business_kpis.json").exists(), "business_kpis.json not found."
    assert (workflow_dir / "validation" / "validation_results.json").exists(), "validation_results.json not found."
    
    zip_path = packages_dir / f"FinSight_Report_{workflow_id}.zip"
    assert zip_path.exists(), f"ZIP package {zip_path.name} not found."
    
    print("--- E2E Test Completed Successfully! ---")
    print(f"All components verified. Workflow ID: {workflow_id}")
