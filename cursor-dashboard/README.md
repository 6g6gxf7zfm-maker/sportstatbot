# SportStatBot Cursor Dashboard

A comprehensive, AI-powered writing assistant dashboard for sports journalists and content creators. Built with React, TypeScript, and integrated with the SportStatBot backend.

## Features

### 🎨 Custom Dashboard
- **League Tabs**: Quick switching between NFL, NBA, MLB, NHL, MLS, Soccer, and Golf
- **Story Queue Management**: Track all your stories from draft to publication
- **Multi-view Interface**: Editor, Queue, Agent Logs, and Writing History panels

### ⌨️ Command Palette (⌘K)
Fuzzy search command system with instant access to:
- Generate digest, preview, feature, or betting stories
- Export to Google Docs (⌘G)
- Run game simulations
- Refresh sports data
- And more...

### 📝 Story Templates
Pre-built templates optimized for different content types:
- **Daily Digest** (800-1200 words): Comprehensive game overview
- **Game Preview** (400-600 words): Upcoming matchup analysis
- **Feature Story** (600-900 words): In-depth trend/player analysis
- **Betting Snapshot** (300-500 words): Odds and recommendations

### ✍️ Advanced Editor
- **Color-coded data states**:
  - 🟡 Yellow: Data missing
  - 🔵 Blue: Data verified
  - 🔴 Red: Data stale
- **Inline data injection**: Hover to expand stat context
- **Auto-paragraph expander** (⌘E): AI-powered content expansion
- **Word count tracker** with customizable limits
- **Full-screen mode** for distraction-free writing

### 🤖 AI Co-Author Sidebar
Real-time AI assistance while you write:
- Contextual paragraph suggestions
- Data-backed recommendations
- Confidence scoring
- One-click insertion

### 📊 Writing Feedback Bot
Automated quality checks:
- Sentence length analysis
- Missing data window detection
- Grammar and structure validation
- House style compliance

### ✅ Real-time Proofreading
- Grammar checking
- Spelling verification
- Style suggestions
- Clarity improvements

### 🔍 Fact-Check System
- Inline hover tooltips
- Source verification links
- Data freshness indicators
- ESPN API integration

### 📈 Agent Activity Logs
Track what's happening behind the scenes:
- Data Fetcher activity
- Analyzer operations
- Formatter actions
- Writer processes

### 📊 Writing History Dashboard
Track your productivity:
- Daily story count
- Total word output
- Average metrics
- Visual charts

### 🚀 Export Options
- **Google Docs** (⌘G): Direct export with formatting
- **Markdown**: Download as .md file
- **Clipboard**: Quick copy
- **Preview**: Review before export

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- ESPN API key (optional)
- The Odds API key (optional)
- Google Docs API credentials (optional)

### Frontend Setup

```bash
cd cursor-dashboard

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your API keys
# VITE_API_URL=http://localhost:8000
# ESPN_API_KEY=your_key_here
# ODDS_API_KEY=your_key_here

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Backend Setup

```bash
cd cursor-dashboard/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ESPN_API_KEY=your_key_here
export ODDS_API_KEY=your_key_here

# Start API server
python api_server.py
```

The API will run at `http://localhost:8000`

## Usage

### Quick Start

1. **Launch both servers**:
   ```bash
   # Terminal 1 - Frontend
   cd cursor-dashboard && npm run dev

   # Terminal 2 - Backend
   cd cursor-dashboard/backend && python api_server.py
   ```

2. **Open dashboard**: Navigate to `http://localhost:3000`

3. **Select a league**: Click on a league tab (NFL, NBA, etc.)

4. **Create a story**:
   - Press `⌘K` to open command palette
   - Type "Generate" and select a template
   - Or click the "Create New Story" button

5. **Start writing**: The editor opens with AI assistance ready

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` or `Ctrl+K` | Open command palette |
| `⌘G` or `Ctrl+G` | Export to Google Docs |
| `⌘S` or `Ctrl+S` | Save current story |
| `⌘E` or `Ctrl+E` | Expand current paragraph |
| `⌘R` or `Ctrl+R` | Run game simulation |
| `⌘⇧R` or `Ctrl+Shift+R` | Refresh sports data |

### Workflow Example

1. **Morning**: Select NFL, create daily digest
2. **Review**: Check AI co-author suggestions in sidebar
3. **Edit**: Use color-coded indicators to verify all data
4. **Polish**: Review writing feedback for improvements
5. **Export**: Preview and export to Google Docs
6. **Track**: Check writing history to monitor productivity

## Architecture

### Frontend Stack
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **Zustand**: State management
- **TanStack Query**: Server state
- **Slate**: Rich text editor
- **cmdk**: Command palette
- **Framer Motion**: Animations

### Backend Stack
- **Flask**: Python web framework
- **SportStatBot**: Core sports data engine
- **ESPN API**: Live sports data
- **The Odds API**: Betting information

### Data Flow
```
User Input → Command Palette → API Request → SportStatBot
                ↓
         Agent Processing
                ↓
    Data Fetcher → Analyzer → Formatter → Writer
                ↓
         API Response → Dashboard → Editor
```

## File Structure

```
cursor-dashboard/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.tsx
│   │   ├── CommandPalette.tsx
│   │   ├── StoryEditor.tsx
│   │   ├── AICoAuthorSidebar.tsx
│   │   └── ...
│   ├── services/           # API integration
│   │   ├── api.ts
│   │   └── googleDocs.ts
│   ├── hooks/              # Custom React hooks
│   │   └── useSportsData.ts
│   ├── store/              # State management
│   │   └── useDashboardStore.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── styles/             # Global styles
│   │   └── globals.css
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── backend/
│   ├── api_server.py       # Flask API server
│   └── requirements.txt
├── public/                 # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## API Endpoints

### Sports Data
- `GET /api/sports/data?sport={SPORT}` - Fetch sports data
- `POST /api/stories/generate` - Generate story content
- `POST /api/stories/expand` - Expand paragraph with AI

### Writing Assistance
- `POST /api/writing/feedback` - Get writing feedback
- `POST /api/writing/proofread` - Real-time proofreading
- `POST /api/ai/coauthor/suggest` - Get AI suggestions

### Export
- `POST /api/export/google-docs` - Export to Google Docs
- `POST /api/export/markdown` - Export as Markdown

### Utilities
- `GET /api/logs` - Get agent activity logs
- `POST /api/fact-check` - Verify fact against sources
- `GET /api/health` - Health check

## Development

### Running Tests
```bash
npm run test           # Frontend tests
npm run type-check     # TypeScript validation
npm run lint           # ESLint
```

### Building for Production
```bash
npm run build          # Creates dist/ folder
npm run preview        # Preview production build
```

### Code Style
- Use TypeScript for all new files
- Follow React hooks best practices
- Keep components focused and reusable
- Use Zustand for global state
- Use TanStack Query for server state

## Customization

### Adding New Templates
Edit `src/components/TemplateModal.tsx`:
```typescript
const templates = [
  {
    id: 'custom',
    name: 'Custom Template',
    description: 'Your description',
    icon: <YourIcon size={32} />,
    estimatedLength: '500-700 words',
  },
  // ... existing templates
];
```

### Adding Command Palette Commands
Edit `src/components/CommandPalette.tsx`:
```typescript
const commands: CommandItem[] = [
  {
    id: 'your-command',
    label: 'Your Command',
    description: 'What it does',
    category: 'generate',
    action: async () => {
      // Your action
    },
  },
  // ... existing commands
];
```

### Customizing Color Scheme
Edit `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      'data-missing': '#your-color',
      'data-verified': '#your-color',
      'data-stale': '#your-color',
    },
  },
}
```

## Troubleshooting

### Dashboard won't load
1. Check that both frontend and backend servers are running
2. Verify API_URL in `.env` matches backend port
3. Check browser console for errors

### API errors
1. Verify ESPN_API_KEY and ODDS_API_KEY are set
2. Check backend logs: `cursor-dashboard/backend/api_server.py`
3. Test API directly: `curl http://localhost:8000/api/health`

### Export not working
1. Verify Google Docs API credentials
2. Check network tab for API errors
3. Ensure sufficient API quota

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [github.com/yourrepo/issues]
- Documentation: [docs.sportstatbot.com]
- Email: support@sportstatbot.com

## Roadmap

### Planned Features
- [ ] Multi-user collaboration
- [ ] Custom AI training on writing style
- [ ] Integration with CMS platforms
- [ ] Mobile app version
- [ ] Advanced analytics dashboard
- [ ] Voice dictation support
- [ ] Automated publishing workflows
- [ ] SEO optimization suggestions

## Credits

Built with ❤️ by the SportStatBot team

Special thanks to:
- ESPN API for sports data
- The Odds API for betting information
- The open-source community
