import { EditorNode } from './node';

type EditorCanvasProps = {
  triggerConf: {
    id: string;
    label: string;
  };
  actionConf: {
    id: string;
    label: string;
  };
};

// function NodeList() {}

// function AddNodeButton() {}

function EditorCanvas(props: EditorCanvasProps) {
  const { actionConf, triggerConf } = props;
  return (
    <div>
      <EditorNode id={triggerConf.id} label={triggerConf.label} type="trigger" onClick={() => {}} />
      <EditorNode id={actionConf.id} label={actionConf.label} type="action" onClick={() => {}} />
    </div>
  );
}

export { EditorCanvas };
