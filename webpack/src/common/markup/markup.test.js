import { rules, makeParser, parseText, renderText } from './index.js'

const cases = {
  title: [
    '@tit: Hello World',
    [{ type: 'blockTag', tag: 'tit', children: ['Hello World'] }],
  ],
  paragraph: [
    'Hello World',
    [{ type: 'paragraph', children: ['Hello World'] }],
  ],
  place: ['[[ here ]]', [{ type: 'place', name: 'here' }]],
  'place flag': [
    '[[ here | left ]]',
    [{ type: 'place', name: 'here', flags: 'left' }],
  ],
  quote: [
    '@sitat: Hello\n@txt: World',
    [{ type: 'pullquote', children: [{ type: 'paragraph' }, { tag: 'txt' }] }],
  ],
  'quote split': [
    '@sitat: Hello\n\n@sitatbyline: World',
    [
      {
        type: 'pullquote',
        children: [{ type: 'paragraph', children: ['Hello'] }],
      },
      { type: 'blockTag' },
    ],
  ],
  faktaboks: [
    '@fakta: her er fakta\n# foo1\n# foo2\n\n@mt: mellomtittel',
    [{ type: 'aside', children: [{}, {}, {}] }, { tag: 'mt' }],
  ],
  place: ['[[ faktaboks 1 ]]', [{ type: 'place', name: 'faktaboks 1' }]],
  link: ['[hi]', [{ children: [{ children: ['hi'], name: 'hi' }] }]],
  'full link': [
    '[hello–](//world.com)',
    [{ children: [{ children: ['hello–'], name: '//world.com' }] }],
  ],
  'partial link': [
    '[hello](//world',
    [{ children: [{ children: ['hello'], name: 'hello' }, '(//world'] }],
  ],
  'two links': [
    '[one](first) foo [two](second)',
    [{ children: [{ name: 'first' }, ' foo ', { name: 'second' }] }],
  ],
  'another partial link': [
    'hello [world',
    [{ children: ['hello ', {}, 'world'] }],
  ],
  emphasis: [
    'hello _world_!',
    [{ children: ['hello ', { type: 'em', children: ['world'] }, '!'] }],
  ],
}

describe('parseText', () => {
  for (const c in cases)
    test(c, () => expect(parseText(cases[c][0])).toMatchObject(cases[c][1]))
})

describe('inline text newline', () => {
  test('white space', () => {
    const text = 'hello\n  world'
    const parsed = parseText(text, false)
    const result = ['hello', { type: 'space' }, 'world']
    expect(parsed).toMatchObject(result)
    expect(renderText(parsed)).toEqual('hello world')
  })
  test('new line', () => {
    const text = 'hello\n\nworld'
    const parsed = parseText(text, false)
    const result = ['hello', { type: 'newline' }, 'world']
    expect(parsed).toMatchObject(result)
    expect(renderText(parsed)).toEqual(text)
  })
})

describe('renderText', () => {
  const reverse = R.pipe(
    parseText,
    renderText,
  )

  for (const c in cases)
    test(c, () => expect(reverse(cases[c][0])).toEqual(cases[c][0]))

  test('cleanup after', () => {
    const SPACE = /\u2060\xa0/g
    expect(reverse('hello _world_, [link]')).toEqual('hello _world_, [link]')
    expect(reverse('-hi \n@mt:- hi. -hi!').replace(SPACE, ' ')).toEqual(
      '– hi\n\n@mt: – hi. – hi!',
    )
    expect(reverse('"hello "world""')).toEqual('«hello «world»»')
    expect(reverse('"hello" "world"')).toEqual('«hello» «world»')
  })
})

test('makeParser', () => {
  const parser = makeParser({ pattern: /he/, type: 'greeting' })
  expect(parser('hei')).toMatchObject({
    content: 'he',
    type: 'greeting',
  })
  expect(parser('ei')).toEqual(null)
})

describe('rules', () => {
  const expected = expect.objectContaining({
    type: expect.any(String),
    order: expect.any(Number),
    pattern: expect.any(RegExp),
    reverse: expect.any(Function),
    inline: expect.any(Boolean),
    leaf: expect.any(Boolean),
  })
  R.forEach(
    rule => test(rule.type, () => expect(rule).toEqual(expected)),
    R.values(rules),
  )
})
