import type { Answer, Result, Sources } from './app.contract.d.ts';
import { SECTIONS, TOC } from './book.gen.ts';

// The book is the site's own, fixed when it is built (content/ → tools/gen-book.ts → book.gen.ts),
// so it reaches nothing.
export const grants = '';

type Section = Result<'loadSection'>;
const EMPTY: Section = {
  id: '', number: '', title: '', chapter: 0, chapterTitle: '', summary: '', blocks: [], outline: [],
  prevId: '', prevTitle: '', nextId: '', nextTitle: '', position: 0, total: 0,
};

const sources: Sources = {
  loadToc: async () => TOC,
  sectionIds: async () => SECTIONS.map(s => s.id),
  loadSection: async ([id]): Promise<Section> => SECTIONS.find(s => s.id === id) ?? EMPTY,
};
export const answer: Answer = (source, args, store, storage, native) => sources[source](args, store, storage, native);
