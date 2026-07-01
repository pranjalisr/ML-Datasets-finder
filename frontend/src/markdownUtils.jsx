export function parseMarkdown(markdown) {
  return markdown.split('\n').map((line, idx) => {
    // Skip empty lines
    if (line.trim() === '' || line === '---') {
      return { type: 'empty', content: '', idx };
    }

    // Headings
    if (line.startsWith('##')) {
      const level = line.match(/^#+/)[0].length;
      const text = line.replace(/^#+\s/, '').trim();
      return { type: `h${level}`, content: text, idx };
    }

    // Code blocks
    if (line.startsWith('```')) {
      return { type: 'code-fence', content: line, idx };
    }

    // Lists
    if (line.match(/^\s*[-*]\s/)) {
      return { type: 'li', content: line.replace(/^\s*[-*]\s/, '').trim(), idx };
    }

    // Bold and italic in regular text
    return { type: 'p', content: line, idx };
  });
}

export function renderContent(element) {
  if (element.type === 'empty') {
    return null;
  }

  if (element.type === 'h2') {
    return (
      <h3 key={element.idx} className="section-title">
        {element.content}
      </h3>
    );
  }

  if (element.type === 'h3') {
    return (
      <h4 key={element.idx} className="subsection-title">
        {element.content}
      </h4>
    );
  }

  if (element.type === 'li') {
    return (
      <li key={element.idx} className="result-item">
        {element.content}
      </li>
    );
  }

  if (element.type === 'code-fence') {
    return null; // Skip fence markers
  }

  if (element.type === 'p') {
    // Handle bold text
    const parts = element.content.split(/(\*\*[^*]+\*\*)/);
    return (
      <p key={element.idx} className="result-text">
        {parts.map((part, i) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={i}>{part.slice(2, -2)}</strong>;
          }
          return part;
        })}
      </p>
    );
  }

  return null;
}