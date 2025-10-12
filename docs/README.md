# BlueTrace Documentation

Next.js-based documentation site for BlueTrace API.

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Visit http://localhost:3000

## Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Structure

```
app/
├── layout.tsx           # Root layout with navigation
├── page.mdx            # Home page
├── quickstart/         # Getting started guide
├── pricing/            # Pricing page
└── api/v1/             # API endpoint documentation
    ├── tides/
    ├── sst/
    ├── currents/
    ├── turbidity/
    └── bathy/
```

## Adding Documentation

1. Create new `.mdx` file in appropriate directory
2. Add navigation link in `layout.tsx`
3. Use Tailwind classes for styling
4. Include code examples with syntax highlighting

## Styling

- Tailwind CSS for utility classes
- Custom components in `globals.css`
- MDX for content with React components

