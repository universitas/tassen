import { makeFuzzer } from 'utils/text'

const [leaf, inline] = [true, true]

export const TAGS = [
  'txt',
  'tingo',
  'mt',
  'bl',
  'ing',
  'tit',
  'tema',
  'sitatbyline',
  'spm',
  'fakta',
  'faktatit',
  'sitat',
]

const tagFuzzer = makeFuzzer(TAGS, 0.5)

const baseRules = {
  whitespace: {
    pattern: /\s+/m,
    order: 0,
  },
  escaped: {
    inline,
    order: 0,
    type: 'character',
    pattern: /\\(\W)/,
  },
  character: {
    inline,
    leaf,
    pattern: /./,
    order: 999,
  },
  text: {
    inline,
    leaf,
    pattern: /[^\n\\_[]+/,
    order: 0,
  },
  link: {
    inline,
    pattern: /\[(?<content>.*?)\](\((?<ref>.*)\))?/,
    reverse: ({ ref, content }) =>
      ref != content ? `[${content}](${ref})` : `[${content}]`,
    process: ({ ref, ...node }) => ({
      ref: ref || node.content,
      ...node,
    }),
  },
  em: {
    inline,
    pattern: /_(?<content>.*?)_/,
    reverse: ({ content }) => `_${content}_`,
  },
  place: {
    leaf,
    pattern: /^ *\[\[ *(?<name>.*?) ( *\| *(?<flags>.*?))? *\]\] *$/,
    reverse: ({ name, flags = '' }) =>
      `\n[[ ${name}${flags && ' | '}${flags} ]]\n`,
  },
  blockTag: {
    pattern: /^@(?<tag>[^:]*): ?(?<content>.*)$/,
    reverse: ({ tag, content }) => {
      const space = R.contains(tag, ['mt', 'spm', 'tingo']) ? '\n' : ''
      return `${space}@${tag}: ${content}`
    },
    process: R.evolve({ tag: tagFuzzer }),
  },
  listItem: {
    pattern: /^(\* |# |@li:) *(?<content>.*)$/,
    order: 9,
    reverse: ({ content }) => `# ${content}`,
  },
  paragraph: {
    pattern: /^.*$/,
    order: 100,
  },
  facts: {
    pattern: /^@fakta:\s?(?<content>(\n?.+)+)$/,
    order: 1,
    reverse: ({ content }) => `\n@fakta: ${content}\n`,
  },
  pullquote: {
    pattern: /^@sitat:\s?(?<content>(\n?.+)+)$/,
    order: 1,
    reverse: ({ content }) => `\n@sitat: ${content}\n`,
  },
}

const defaultRule = {
  order: 10,
  leaf: false,
  inline: false,
  reverse: R.propOr('[NO CONTENT]', 'content'),
}

export default R.pipe(
  R.map(R.merge(defaultRule)),
  R.mapObjIndexed((val, type, obj) => ({ type, ...val })),
)(baseRules)