```jsx
const nodes = [
  { id: 'camera1', x: 100, y: 150 },
  { id: 'camera2', x: 300, y: 150 },
  { id: 'camera3', x: 200, y: 300 }
];

const links = [
  { source: 'camera1', target: 'camera2' },
  { source: 'camera2', target: 'camera3' },
  { source: 'camera3', target: 'camera1' }
];

const ConstellationGraph = () => {
  return (
    <svg width="500" height="400">
      {nodes.map(node => (
        <circle
          key={node.id}
          cx={node.x}
          cy={node.y}
          r="20"
          fill="#0ea5e9"
        />
      ))}
      {links.map(link => {
        const sourceNode = nodes.find(n => n.id === link.source);
        const targetNode = nodes.find(n => n.id === link.target);
        return (
          <line
            key={`${link.source}-${link.target}`}
            x1={sourceNode.x}
            y1={sourceNode.y}
            x2={targetNode.x}
            y2={targetNode.y}
            stroke="#334155"
            strokeWidth="2"
          />
        );
      })}
    </svg>
  );
};

export default ConstellationGraph;
```