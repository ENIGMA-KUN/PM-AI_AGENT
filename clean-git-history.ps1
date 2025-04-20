# PowerShell script to clean Git history of sensitive files
# This follows windsurf project structure requirements for secure repository management

Write-Host "Starting Git history cleaning process..." -ForegroundColor Cyan

# Step 1: Ensure .gitignore is properly configured
$gitignoreContent = Get-Content -Path ".gitignore"
$requiredEntries = @('.env', 'google-calendar.json', 'project_*.json')

foreach ($entry in $requiredEntries) {
    if ($gitignoreContent -notcontains $entry) {
        Write-Host "Adding $entry to .gitignore..." -ForegroundColor Yellow
        Add-Content -Path ".gitignore" -Value $entry
    }
}

# Step 2: Update project_log.md with this security operation
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$logEntry = "- **$timestamp**: Security: Removed sensitive credentials from Git history"
Add-Content -Path "project_log.md" -Value $logEntry

# Step 3: Create a new branch for the cleaned history
Write-Host "Creating a new clean branch..." -ForegroundColor Cyan
git checkout --orphan temp_clean_branch

# Step 4: Add all files from the working directory
Write-Host "Adding all current files (without history)..." -ForegroundColor Cyan
git add --all

# Step 5: Commit the current state
Write-Host "Committing current state without sensitive data..." -ForegroundColor Cyan
git commit -m "Initial commit: Clean repository without sensitive data"

# Step 6: Delete the old branch
Write-Host "Removing old branch with sensitive data..." -ForegroundColor Cyan
git branch -D main

# Step 7: Rename the new branch to main
Write-Host "Renaming clean branch to main..." -ForegroundColor Cyan
git branch -m main

# Step 8: Force push to replace the remote repository
Write-Host "Ready to force push the cleaned repository..." -ForegroundColor Green
Write-Host "Run the following command to push: git push -f origin main" -ForegroundColor Yellow
