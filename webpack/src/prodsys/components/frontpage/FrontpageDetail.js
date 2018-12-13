import { connect } from 'react-redux'
import cx from 'classnames'
import StyleButtons from './StyleButtons.js'
import Debug from 'components/Debug'
import GridWidget from './GridWidget.js'
import ModelField from 'components/ModelField'
import { FrontpageTools } from '.'
import { MODEL, Field, selectors, actions } from './model.js'
import DetailPanel from 'components/DetailPanel'

// Cropbox field connected to the related photo instance
const CropBox = connect(
  (state, { pk }) => selectors.getItem(pk)(state),
  dispatch => ({
    changeHandler: (pk, name) => value =>
      dispatch(actions.fieldChanged(pk, name, value)),
  }),
)(({ id, image_id, crop_box, changeHandler }) => {
  return image_id ? (
    <ModelField
      editable
      pk={image_id}
      onChange={changeHandler(id, 'crop_box')}
      value={crop_box /* we update and read through frontpage api endpoint */}
      type="cropbox"
      name="crop_box"
      model="photos"
      label="beskjæring"
    />
  ) : null
})

const FrontpageDetail = ({ pk }) => (
  <DetailPanel pk={pk} model={MODEL} getTitle={R.prop('headline')}>
    {pk ? (
      <React.Fragment>
        <Field pk={pk} name="vignette" editable />
        <Field pk={pk} name="kicker" editable />
        <Field pk={pk} name="headline" editable />
        <Field pk={pk} name="lede" editable />
        <Field pk={pk} name="priority" editable />
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <StyleButtons pk={pk} />
          <GridWidget pk={pk} />
        </div>
        <Field key={pk} pk={pk} name="image_id" editable />
        <CropBox pk={pk} />
      </React.Fragment>
    ) : (
      <div>velg en sak</div>
    )}
  </DetailPanel>
)

export default FrontpageDetail