import { Container } from 'react-bootstrap';

import Header from './components/Header';
import Footer from './components/Footer';

import HomeScreen from './screens/HomeScreen';
import ProductScreen from './screens/ProductScreen';  
import ChatbotScreen from './screens/ChatbotScreen';
import UserScreen from './screens/UserScreen';
import ProtectedRoute from './components/ProtectedRoute';

import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Header />
      <main className='py-3'>

        <Container>
          <Routes>
            <Route path='/User' element={<UserScreen />} />

            <Route path='/' element={<ProtectedRoute><HomeScreen /></ProtectedRoute>} exact />
            <Route path='/product/:id' element={<ProtectedRoute><ProductScreen /></ProtectedRoute>} />
            <Route path='/chat' element={<ProtectedRoute><ChatbotScreen /></ProtectedRoute>} />
          </Routes>
        </Container>

      </main>
      <Footer />
    </Router>
  );
}

export default App;
