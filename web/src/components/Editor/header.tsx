import { Button } from '../ui/button';
import { Input } from '../ui/input';

type EditorHeaderProps = {
  name: string;
  onNameChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSaveDraft?: () => void;
  onTestWorkflow?: () => void;
  onPublishWorkflow?: () => void;
};

function EditorHeader(props: EditorHeaderProps) {
  const { name, onNameChange } = props;

  return (
    <header className="flex p-2 justify-between">
      <div>
        <Input value={name} onChange={onNameChange} />
      </div>
      <div className="flex space-x-2">
        <Button>Test</Button>
        <Button>Save</Button>
        <Button>Publish</Button>
      </div>
    </header>
  );
}

export { EditorHeader };
