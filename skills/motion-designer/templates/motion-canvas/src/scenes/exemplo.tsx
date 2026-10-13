import {makeScene2D, Circle, Txt} from '@motion-canvas/2d';
import {all, createRef} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  view.fill('#0a0a0a');
  const bola = createRef<Circle>();
  const txt = createRef<Txt>();
  view.add(<Circle ref={bola} size={0} fill={'#3c83f6'} />);
  view.add(<Txt ref={txt} text={'Legacy'} fill={'#ffffff'} fontSize={120} opacity={0} y={260} />);
  yield* bola().size(320, 0.8);
  yield* all(txt().opacity(1, 0.6), bola().fill('#17adfd', 0.6));
});
