import { hot } from 'react-hot-loader'
import 'styles/universitas.scss'
import TopMenu from 'components/TopMenu'
import PageSwitch from 'components/PageSwitch'
import FrontpageEdit from 'components/FrontpageEdit'

const App = ({}) => (
  <div className="Universitas">
    <TopMenu />
    <PageSwitch />
    <FrontpageEdit />
  </div>
)

export default hot(module)(App)
