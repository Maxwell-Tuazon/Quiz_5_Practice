import React, { useState } from 'react'
import { Form, Button, Row, Col } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function UserScreen() {
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const submitHandler = async (e) => {
    e.preventDefault()
    try {
      // Attempt login first using name as username
      const { data } = await axios.post('/api/users/login/', { username: name, password })
      localStorage.setItem('userInfo', JSON.stringify(data))
      navigate('/')
    } catch (loginError) {
      try {
        // If login failed, register the user
        const { data } = await axios.post('/api/users/register/', { name, password })
        localStorage.setItem('userInfo', JSON.stringify(data))
        navigate('/')
      } catch (regError) {
        const msg = regError.response && regError.response.data.detail ? regError.response.data.detail : regError.message
        alert('Authentication failed: ' + msg)
      }
    }
  }

  return (
    <Row className='justify-content-md-center'>
      <Col xs={12} md={6}>
        <h2>User</h2>
        <Form onSubmit={submitHandler}>
          <Form.Group controlId='name' className='my-2'>
            <Form.Label>Name</Form.Label>
            <Form.Control type='text' placeholder='Enter name (used as username)' value={name} onChange={(e) => setName(e.target.value)} required />
          </Form.Group>
          

          <Form.Group controlId='password' className='my-2'>
            <Form.Label>Password</Form.Label>
            <Form.Control type='password' placeholder='Password' value={password} onChange={(e) => setPassword(e.target.value)} required />
          </Form.Group>

          <Button type='submit' variant='primary' className='my-2'>Sign In / Register</Button>
        </Form>
      </Col>
    </Row>
  )
}

export default UserScreen
