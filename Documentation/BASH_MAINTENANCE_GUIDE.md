# CompuCyto Bash-Based Maintenance System

## 🎯 Overview

CompuCyto now uses **Git Bash** for all maintenance operations, making scripts cleaner, more powerful, and more reliable than traditional Windows batch files.

## 🚀 Why Git Bash?

### ✅ **Advantages over Batch Files:**
- **Cleaner syntax** - easier to read and maintain
- **Better error handling** - `set -e` stops on errors
- **Powerful tools** - grep, awk, sed, curl built-in
- **No PATH issues** - bash handles environment properly
- **Cross-platform** - same scripts work on Linux/Mac
- **Colors support** - beautiful formatted output
- **Real pipes** - proper command chaining
- **Standard commands** - npm, git, psql work naturally

### 📊 **Comparison:**

| Feature | Batch (.bat) | Bash (.sh) |
|---------|-------------|-----------|
| Syntax | Complex, cryptic | Clean, readable |
| Error handling | Manual checking | Built-in `set -e` |
| String manipulation | Limited | Powerful |
| Conditionals | Verbose | Concise |
| Functions | Basic | Full-featured |
| Colors | Difficult | Easy |
| Cross-platform | Windows only | Works everywhere |

## 📁 File Structure

```
CompuCyto/
├── maintenance.bat          # Simple Windows launcher
├── maintenance.sh           # Main bash maintenance script
├── health-monitor.sh        # Auto-generated health monitor
└── SetUp/
    ├── autonomous-setup-windows-v2.bat  # Initial setup (installs Git)
    └── ...
```

## 🎮 How to Use

### Quick Start

**Double-click:** `maintenance.bat`

This launches `maintenance.sh` in Git Bash automatically.

### From Command Line

**Option 1: Via wrapper (Windows)**
```cmd
maintenance.bat
```

**Option 2: Direct bash (if Git Bash is open)**
```bash
./maintenance.sh
```

**Option 3: From Git Bash terminal in VS Code**
```bash
bash maintenance.sh
```

## 🎨 Features

### All the Same Great Features

The bash version has all 25 features from the batch version:

1. **Application Control** - Start, stop, restart, health monitor
2. **Repository Management** - Git operations with smart automation
3. **Dependency Management** - npm operations
4. **Database Operations** - Backups, migrations, restore
5. **System Diagnostics** - Health checks, testing
6. **Utilities** - Cache clearing, reports, VS Code integration

### But Better!

**Color-coded output:**
```bash
✓ Green for success
✗ Red for errors
! Yellow for warnings
i Blue for info
```

**Cleaner error messages:**
```bash
[✗] Backend connection failed!
[i] Attempting to restart...
[✓] Backend restarted successfully!
```

**Better process management:**
```bash
# Instead of:
taskkill /F /IM node.exe

# We use:
pkill -f "nest.*start:dev"
```

**Smarter checks:**
```bash
# Instead of checking exit codes:
if %errorLevel% neq 0 (...)

# We use:
if command -v node &> /dev/null; then
    print_success "OK"
fi
```

## 🔥 Key Improvements

### 1. Health Monitor

**Old batch version:**
- Separate PowerShell script
- Complex process checking
- Hard to read

**New bash version:**
```bash
#!/bin/bash
while true; do
    if curl -s http://localhost:3000/api >/dev/null; then
        echo -e "${GREEN}✓ HEALTHY${NC}"
    else
        echo -e "${RED}✗ DOWN${NC}"
        # Auto-restart logic
    fi
    sleep 30
done
```

### 2. Git Operations

**Batch:**
```batch
git fetch
git pull
if %errorLevel% neq 0 (
    echo Failed
    pause
    exit /b 1
)
```

**Bash:**
```bash
if git pull; then
    print_success "Updated!"
else
    print_error "Failed!"
    return
fi
```

### 3. Database Operations

**Batch:**
```batch
set PGPASSWORD=password
psql -U user -c "SELECT 1"
if %errorLevel% neq 0 (...)
```

**Bash:**
```bash
export PGPASSWORD="password"
if psql -U user -c "SELECT 1" &>/dev/null; then
    print_success "Connected"
fi
```

## 🛠️ Development

### Creating New Functions

Functions are easy to add:

```bash
my_new_function() {
    print_header "My New Feature"
    
    print_info "Doing something..."
    
    if some_command; then
        print_success "Success!"
    else
        print_error "Failed!"
    fi
    
    pause_for_user
}
```

Then add to menu:
```bash
show_menu() {
    echo "    26) My New Feature"
}

main() {
    case $choice in
        26) my_new_function ;;
    esac
}
```

### Helper Functions Available

```bash
print_header "Title"        # Blue header
print_success "Message"     # Green checkmark
print_error "Message"       # Red X
print_info "Message"        # Yellow info
print_warning "Message"     # Yellow warning
pause_for_user              # Wait for Enter
```

## 📚 Bash Basics

### Variables
```bash
MY_VAR="value"
echo "$MY_VAR"
```

### Conditionals
```bash
if [[ "$VAR" == "value" ]]; then
    echo "Match"
fi
```

### Command Success Check
```bash
if command -v node &> /dev/null; then
    echo "Node exists"
fi
```

### Running Commands
```bash
if npm install; then
    echo "Success"
else
    echo "Failed"
fi
```

### Loops
```bash
for file in *.txt; do
    echo "$file"
done

while true; do
    echo "Running..."
    sleep 30
done
```

## 🔄 Migration from Batch

### Old Way (Batch)
```batch
@echo off
set VAR=value
if "%VAR%"=="value" (
    echo Match
)
```

### New Way (Bash)
```bash
#!/bin/bash
VAR="value"
if [[ "$VAR" == "value" ]]; then
    echo "Match"
fi
```

## 🎓 Learning Resources

### Bash Scripting
- [Bash Guide](https://mywiki.wooledge.org/BashGuide)
- [ShellCheck](https://www.shellcheck.net/) - Script validator
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)

### Git Bash on Windows
- [Git for Windows](https://gitforwindows.org/)
- [Git Bash Tutorial](https://www.atlassian.com/git/tutorials/git-bash)

## 🐛 Troubleshooting

### "Git Bash not found"
**Solution:** Install Git for Windows
```
https://git-scm.com/download/win
```

### "Permission denied"
**Solution:** Make script executable
```bash
chmod +x maintenance.sh
```

### "command not found"
**Solution:** Check PATH in bash
```bash
echo $PATH
```

Or add to script:
```bash
export PATH="/c/Program Files/nodejs:$PATH"
```

### Line ending issues
**Solution:** Convert to Unix format
```bash
dos2unix maintenance.sh
```

Or in Git:
```bash
git config --global core.autocrlf input
```

## 🚀 Best Practices

### 1. Use `set -e` at the top
```bash
#!/bin/bash
set -e  # Exit on error
```

### 2. Quote variables
```bash
# Good
cd "$PROJECT_DIR"

# Bad
cd $PROJECT_DIR
```

### 3. Check command existence
```bash
if command -v node &> /dev/null; then
    # Use node
fi
```

### 4. Use functions
```bash
do_something() {
    local var="value"  # Local to function
    echo "$var"
}
```

### 5. Handle errors gracefully
```bash
if ! some_command; then
    print_error "Command failed"
    return 1
fi
```

## 🎯 Next Steps

1. **Learn bash basics** - It's easier than you think!
2. **Customize functions** - Add your own features
3. **Share improvements** - Contribute back to the project
4. **Explore Git Bash** - It has tons of useful tools

## 💡 Pro Tips

### Run Multiple Commands
```bash
npm install && npm run build && npm test
```

### Pipe Output
```bash
ps aux | grep node | grep -v grep
```

### Redirect Output
```bash
npm install > install.log 2>&1
```

### Background Processes
```bash
npm start &  # Run in background
```

### Check Last Command Status
```bash
if [ $? -eq 0 ]; then
    echo "Previous command succeeded"
fi
```

---

**The bash-based maintenance system is more powerful, cleaner, and easier to maintain! 🎉**

## 📞 Support

Questions? Check:
- `maintenance.sh` - Read the source code
- [Bash Guide](https://mywiki.wooledge.org/BashGuide)
- [Git Bash Tutorial](https://www.atlassian.com/git/tutorials/git-bash)
