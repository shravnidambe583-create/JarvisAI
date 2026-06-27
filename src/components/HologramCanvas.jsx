import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars, PerspectiveCamera } from '@react-three/drei'
import Avatar from './Avatar'

// Particle cloud floating effect
function ParticleCloud({ count = 200, hologramMode }) {
  const pointsRef = useRef()

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.getElapsedTime() * 0.05
      pointsRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.02) * 0.05
    }
  })

  // Generate random positions
  const positions = React.useMemo(() => {
    const arr = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 8
      arr[i * 3 + 1] = (Math.random() - 0.5) * 6 + 1
      arr[i * 3 + 2] = (Math.random() - 0.5) * 8
    }
    return arr
  }, [count])

  const color = hologramMode ? '#00f0ff' : '#bf5af2'

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        color={color}
        size={0.05}
        sizeAttenuation
        transparent
        opacity={0.6}
        depthWrite={false}
      />
    </points>
  )
}

// Tech scanline grid at the floor
function FloorGrid({ hologramMode }) {
  const gridColor = hologramMode ? '#00f0ff' : '#bf5af2'
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]}>
      <planeGeometry args={[20, 20]} />
      <meshBasicMaterial
        color={gridColor}
        wireframe
        transparent
        opacity={0.15}
      />
    </mesh>
  )
}

export default function HologramCanvas({ hologramMode, mood, micActive, avatarUrl }) {
  return (
    <div style={{ width: '100vw', height: '100vh', position: 'absolute', top: 0, left: 0, zIndex: 1 }}>
      <Canvas style={{ background: '#020208' }}>
        <PerspectiveCamera makeDefault position={[0, 0.5, 4.5]} fov={55} />
        
        {/* Holographic Stage Lighting */}
        <ambientLight intensity={0.4} />
        <pointLight position={[5, 5, 5]} intensity={1} color="#00f0ff" />
        <pointLight position={[-5, 5, -5]} intensity={0.8} color="#bf5af2" />
        
        {/* Spotlight projecting from bottom */}
        <spotLight 
          position={[0, -2, 0]} 
          angle={0.6} 
          penumbra={1} 
          intensity={3} 
          color={hologramMode ? '#00f0ff' : '#bf5af2'} 
          castShadow
        />

        {/* 3D Animated Avatar Model */}
        <Avatar 
          hologramMode={hologramMode} 
          mood={mood} 
          micActive={micActive} 
          avatarUrl={avatarUrl}
        />

        {/* Ambient VFX */}
        <ParticleCloud count={250} hologramMode={hologramMode} />
        <FloorGrid hologramMode={hologramMode} />
        <Stars radius={100} depth={50} count={300} factor={4} saturation={0.5} fade speed={1.5} />

        <OrbitControls 
          enableZoom={true}
          maxDistance={8}
          minDistance={2}
          maxPolarAngle={Math.PI / 2 + 0.1}
          minPolarAngle={Math.PI / 4}
          target={[0, 0.5, 0]}
        />
      </Canvas>
    </div>
  )
}
