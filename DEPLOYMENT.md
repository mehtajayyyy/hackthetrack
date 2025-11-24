# RaceIQ Pro - Deployment Guide

## Overview

This guide explains how to deploy RaceIQ Pro to free hosting platforms like Streamlit Cloud. The application uses pre-aggregated telemetry data to reduce file size from 3GB to ~50-100MB, making it compatible with free hosting tiers.

## Prerequisites

- Python 3.8 or higher
- Access to the raw telemetry CSV files (for preprocessing)
- Git repository (for deployment)

## Step 1: Preprocess Telemetry Data

Before deploying, you need to preprocess the large telemetry CSV files into aggregated Parquet format.

### Run the Preprocessing Script

```bash
# Install required dependencies
pip install pandas pyarrow

# Run the preprocessing script
python preprocess_telemetry.py
```

This will generate:

- `R1_barber_telemetry_aggregated.parquet` (~25-50MB)
- `R2_barber_telemetry_aggregated.parquet` (~25-50MB)

**Expected Results:**

- Input: 3GB total (1.5GB × 2 files)
- Output: ~50-100MB total (25-50MB × 2 files)
- Reduction: ~95%+ file size reduction

### Verify Generated Files

```bash
# Check file sizes
ls -lh *.parquet

# Verify files exist
ls R*_barber_telemetry_aggregated.parquet
```

## Step 2: Prepare Repository

### Files to Include

**Required Files:**

- `main.py` - Main application entry point
- `config.py` - Configuration
- `data_processing.py` - Data processing functions
- `telemetry.py` - Telemetry processing
- `ui_components.py` - UI components
- `sidebar.py` - Sidebar controls
- `kpis.py` - KPI calculations
- `live_mode.py` - Live mode logic
- `tabs/` - Tab modules directory
- `requirements.txt` - Python dependencies
- `Toyota GR Hackathon Datasets.xlsx` - Main dataset (~434KB)
- `R1_barber_telemetry_aggregated.parquet` - Aggregated telemetry (Race 1)
- `R2_barber_telemetry_aggregated.parquet` - Aggregated telemetry (Race 2)

**Files to Exclude (add to .gitignore):**

- `R1_barber_telemetry_data.csv` - Raw CSV (1.5GB - too large)
- `R2_barber_telemetry_data.csv` - Raw CSV (1.5GB - too large)
- `*.pyc` - Python cache files
- `__pycache__/` - Python cache directories
- `.venv/` or `venv/` - Virtual environment
- `.streamlit/` - Streamlit config (optional)

### Create .gitignore

```bash
# Create .gitignore file
cat > .gitignore << EOF
# Large telemetry files (use aggregated versions instead)
R1_barber_telemetry_data.csv
R2_barber_telemetry_data.csv

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Streamlit
.streamlit/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

## Step 3: Deploy to Streamlit Cloud

### Option A: Deploy via Streamlit Cloud UI

1. **Push to GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit - RaceIQ Pro"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Connect to Streamlit Cloud:**

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `main.py`
   - Click "Deploy"

3. **Configure App:**
   - The app will automatically detect `requirements.txt`
   - Streamlit Cloud will install dependencies
   - First deployment may take 5-10 minutes

### Option B: Deploy via Streamlit CLI

```bash
# Install Streamlit CLI (if not already installed)
pip install streamlit

# Deploy (requires Streamlit Cloud account setup)
streamlit deploy
```

## Step 4: Verify Deployment

After deployment, verify:

1. **App loads successfully**

   - Check that the app loads without errors
   - Verify all tabs are accessible

2. **Data loads correctly**

   - Select Race 1 or Race 2
   - Verify KPIs display correctly
   - Check that telemetry data loads (Overview tab)

3. **All features work**
   - Test vehicle filter
   - Test lap slider
   - Test live mode
   - Verify all tabs render correctly

## Troubleshooting

### Issue: "File not found" errors

**Solution:** Ensure aggregated Parquet files are committed to the repository:

```bash
git add R*_barber_telemetry_aggregated.parquet
git commit -m "Add aggregated telemetry files"
git push
```

### Issue: "Module not found" errors

**Solution:** Verify `requirements.txt` includes all dependencies:

```bash
# Check requirements.txt
cat requirements.txt

# Test locally first
pip install -r requirements.txt
streamlit run main.py
```

### Issue: App is slow to load

**Solution:** This is normal for first load. Streamlit Cloud caches data after first load. Subsequent loads will be faster.

### Issue: Memory errors

**Solution:** The aggregated files should be small enough. If issues persist:

- Verify aggregated files are being used (check `config.py`: `USE_AGGREGATED_TELEMETRY = True`)
- Ensure raw CSV files are NOT in the repository

## Alternative Hosting Options

### Railway

1. Create account at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add `Procfile`:
   ```
   web: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
   ```
4. Deploy

### Heroku

1. Create account at [heroku.com](https://heroku.com)
2. Install Heroku CLI
3. Create `Procfile`:
   ```
   web: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
   ```
4. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Render

1. Create account at [render.com](https://render.com)
2. Connect GitHub repository
3. Create new Web Service
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`

## File Size Limits

| Platform        | Free Tier Limit | Our Files |
| --------------- | --------------- | --------- |
| Streamlit Cloud | 1GB             | ~100MB ✅ |
| Railway         | 500MB           | ~100MB ✅ |
| Heroku          | 500MB           | ~100MB ✅ |
| Render          | 1GB             | ~100MB ✅ |

## Post-Deployment

### Update Documentation

After successful deployment:

1. Update `README.md` with deployment URL
2. Add deployment badge (optional)
3. Document any platform-specific configurations

### Monitor Performance

- Check Streamlit Cloud metrics
- Monitor memory usage
- Track load times
- Gather user feedback

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review application logs in Streamlit Cloud
3. Test locally first before deploying
4. Verify all files are committed correctly
