import { Button } from '../ui/button';
import { Card, CardFooter, CardHeader, CardTitle } from '../ui/card';

type EditorNodeProps = {
  id: string;
  type: 'trigger' | 'action';
  label: string;
  onClick: (id: string) => void;
};

function EditorNode(props: EditorNodeProps) {
  const { id, label, onClick, type } = props;

  return (
    <Card id={id}>
      <CardHeader>
        <p>{type}</p>
        <CardTitle>{label}</CardTitle>
      </CardHeader>
      <CardFooter>
        <Button onClick={() => onClick(id)}>Configure</Button>
      </CardFooter>
    </Card>
  );
}

export { EditorNode };
