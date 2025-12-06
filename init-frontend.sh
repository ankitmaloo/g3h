#!/bin/bash

# Frontend Initialization Script
# Creates a Vite + React + TypeScript + shadcn/ui project in the frontend folder
#
# Usage:
#   ./init-frontend.sh           # Run with prompts
#   ./init-frontend.sh --dry-run # Preview what will happen (no changes)
#   ./init-frontend.sh --force   # Skip confirmation, backup existing folder

set -e  # Exit on error

FRONTEND_DIR="frontend"
DRY_RUN=false
FORCE=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      ;;
    --force)
      FORCE=true
      ;;
  esac
done

# Dry run mode
if [ "$DRY_RUN" = true ]; then
  echo "🔍 DRY RUN MODE - No changes will be made"
  echo ""
  echo "This script will:"
  echo "  1. Create Vite + React + TypeScript project in ./$FRONTEND_DIR"
  echo "  2. Install npm dependencies"
  echo "  3. Add Tailwind CSS with @tailwindcss/vite"
  echo "  4. Add @types/node"
  echo "  5. Add Radix UI primitives (dialog, dropdown-menu, tooltip, tabs, etc.)"
  echo "  6. Configure Tailwind CSS in src/index.css"
  echo "  7. Configure tsconfig.json with @/* path aliases"
  echo "  8. Configure tsconfig.app.json with path aliases"
  echo "  9. Configure vite.config.ts with path resolution"
  echo "  10. Initialize shadcn/ui"
  echo "  11. Add shadcn button and card components"
  echo "  12. Create sample App.tsx"
  echo ""
  if [ -d "$FRONTEND_DIR" ]; then
    echo "⚠️  WARNING: ./$FRONTEND_DIR already exists!"
    echo "   Running without --dry-run will backup to ./${FRONTEND_DIR}_backup_<timestamp>"
  fi
  echo ""
  echo "To run for real: ./init-frontend.sh"
  echo "To run and skip prompts: ./init-frontend.sh --force"
  exit 0
fi

# Check if frontend folder already exists
if [ -d "$FRONTEND_DIR" ]; then
  echo "⚠️  WARNING: ./$FRONTEND_DIR already exists!"
  echo ""
  
  if [ "$FORCE" = false ]; then
    echo "Options:"
    echo "  1) Backup existing folder and continue"
    echo "  2) Abort"
    echo ""
    read -p "Choose (1 or 2): " choice
    
    case $choice in
      1)
        BACKUP_DIR="${FRONTEND_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        echo ""
        echo "📦 Backing up to ./$BACKUP_DIR..."
        mv "$FRONTEND_DIR" "$BACKUP_DIR"
        echo "✅ Backup created!"
        ;;
      *)
        echo "❌ Aborted."
        exit 1
        ;;
    esac
  else
    # Force mode: auto-backup
    BACKUP_DIR="${FRONTEND_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    echo "📦 Backing up to ./$BACKUP_DIR..."
    mv "$FRONTEND_DIR" "$BACKUP_DIR"
    echo "✅ Backup created!"
  fi
fi

echo ""
echo "🚀 Initializing frontend in ./$FRONTEND_DIR..."

# Step 1: Create Vite project with React + TypeScript
echo ""
echo "📦 Step 1: Creating Vite project with React + TypeScript..."
npm create vite@latest $FRONTEND_DIR -- --template react-ts

cd $FRONTEND_DIR

# Step 2: Install dependencies
echo ""
echo "📦 Step 2: Installing dependencies..."
npm install

# Step 3: Add Tailwind CSS with Vite plugin
echo ""
echo "🎨 Step 3: Adding Tailwind CSS..."
npm install tailwindcss @tailwindcss/vite

# Step 4: Add @types/node for path resolution
echo ""
echo "📦 Step 4: Adding @types/node..."
npm install -D @types/node

# Step 5: Add Radix UI primitives
echo ""
echo "🎯 Step 5: Adding Radix UI primitives..."
npm install @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-tooltip \
  @radix-ui/react-tabs \
  @radix-ui/react-accordion \
  @radix-ui/react-popover \
  @radix-ui/react-select \
  @radix-ui/react-checkbox \
  @radix-ui/react-radio-group \
  @radix-ui/react-switch \
  @radix-ui/react-slider \
  @radix-ui/react-avatar \
  @radix-ui/react-separator \
  @radix-ui/react-label \
  @radix-ui/react-scroll-area \
  @radix-ui/react-toggle \
  @radix-ui/react-toggle-group

# Step 6: Update src/index.css with Tailwind import
echo ""
echo "🎨 Step 6: Configuring Tailwind CSS..."
cat > src/index.css << 'EOF'
@import "tailwindcss";
EOF

# Step 6: Update tsconfig.json with path aliases
echo ""
echo "⚙️  Step 6: Configuring tsconfig.json..."
cat > tsconfig.json << 'EOF'
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ],
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
EOF

# Step 7: Update tsconfig.app.json with path aliases
echo ""
echo "⚙️  Step 7: Configuring tsconfig.app.json..."
cat > tsconfig.app.json << 'EOF'
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
EOF

# Step 8: Update vite.config.ts with path alias and Tailwind plugin
echo ""
echo "⚙️  Step 8: Configuring vite.config.ts..."
cat > vite.config.ts << 'EOF'
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
EOF

# Step 9: Run shadcn init with defaults
echo ""
echo "🎨 Step 9: Initializing shadcn/ui..."
npx shadcn@latest init -d

# Step 10: Add ALL shadcn components
echo ""
echo "🧩 Step 10: Adding ALL shadcn/ui components..."
npx -y shadcn@latest add --all --overwrite

# Step 11: Create a sample App.tsx to verify everything works
echo ""
echo "📝 Step 11: Creating sample App.tsx..."
cat > src/App.tsx << 'EOF'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

function App() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center bg-background p-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome to Your Frontend</CardTitle>
          <CardDescription>
            Vite + React + TypeScript + shadcn/ui + Tailwind CSS
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-muted-foreground">
            Your frontend is ready! Start building something amazing.
          </p>
          <Button>Get Started</Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
EOF

echo ""
echo "✅ Frontend initialization complete!"
echo ""
echo "📁 Project created at: ./$FRONTEND_DIR"
echo ""
echo "🚀 To start the development server:"
echo "   cd $FRONTEND_DIR"
echo "   npm run dev"
echo ""
echo "📚 shadcn/ui components are available. Add more with:"
echo "   npx shadcn@latest add <component-name>"
echo ""
