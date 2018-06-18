import { parseText, rules } from 'markup'

const childTypes = [
  // child types in story redux state
  'images',
  'videos',
  'pullquotes',
  'asides',
  'inline_html_blocks',
]

// :: {story} -> [{storychild}]
export const getChildren = R.pipe(
  R.pick(childTypes),
  R.mapObjIndexed((val, key, obj) =>
    R.map(R.assoc('type', R.replace(/s$/, '', key)), val),
  ),
  R.values,
  R.reduce(R.concat, []),
)

// :: {story} -> ['placement']
export const getPlaces = R.pipe(getChildren, R.pluck('placement'), R.uniq)

// :: linkNode -> {story} -> {inline_html_link}
export const getLink = ({ ref }) =>
  R.pipe(R.prop('links'), R.find(R.propEq('number', parseInt(ref))))

// :: {place} -> {story} -> [{storychild}]
export const getPlaceChildren = ({ name }) =>
  R.pipe(getChildren, R.filter(R.propEq('placement', name)))

// :: {story} -> {...story, nodeTree}
export const buildNodeTree = story => {
  let { title, kicker, lede, theme_word, bylines } = story
  const walk = R.map(parseNode => {
    if (R.is(String, parseNode)) return parseNode
    let { type, children, match, ...props } = parseNode
    if (children) props.children = walk(children)
    switch (type) {
      case 'place':
        props.children = R.pipe(
          getPlaceChildren(parseNode),
          R.sortBy(R.prop('ordering')),
          R.map(
            R.when(R.prop('bodytext_markup'), child => ({
              ...child,
              children: R.pipe(
                R.prop('bodytext_markup'),
                R.replace(/@fakta:/g, '@faktatit:'),
                R.replace(/@sitat:/g, ''),
                parseText,
                walk,
              )(child),
            })),
          ),
        )(story)
        break
      case 'link':
        props.link = getLink(props)(story)
        break
      case 'blockTag':
        switch (props.tag) {
          case 'fakta':
            props.type = 'place'
            props.children = [{ type: 'aside', children }]
            break
          case 'sitat':
            props.type = 'place'
            props.children = [{ type: 'pullquote', children }]
            break
          case 'bl':
            bylines = R.append(parseByline(children[0]), bylines)
            return null
          case 'tit':
            if (!title) {
              title = match[0]
              return null
            }
          case 'tema':
            theme_word = match[0]
            return null
          case 'ing':
            lede += match[0]
            return null
          case 'kicker':
            kicker = match[0]
            return null
        }
        break
    }
    return { type, ...props }
  })

  const parseTree = parseText(story.bodytext_markup)
  const nodeTree = walk(parseTree)

  return {
    ...story,
    title,
    kicker,
    lede,
    theme_word,
    bylines,
    parseTree,
    nodeTree,
  }
}
