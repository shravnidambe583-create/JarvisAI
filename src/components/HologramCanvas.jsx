import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars, PerspectiveCamera } from '@react-three/drei'
import Avatar from './Avatar'
import * as THREE from 'three'

// Floating Starfield / Particles tailored to environments
function CustomEnvironmentParticles({ count = 200, world, mood }) {
  const pointsRef = useRef()

  useFrame((state) => {
    if (pointsRef.current) {
      const speed = world === 'space-station' ? 0.08 : world === 'cyber-city' ? 0.03 : 0.01
      pointsRef.current.rotation.y = state.clock.getElapsedTime() * speed
      pointsRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.01) * 0.05
    }
  })

  const positions = React.useMemo(() => {
    const arr = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      // Space station spreads particles further out, Neon room aggregates them as core dust
      const spread = world === 'space-station' ? 12 : world === 'neon-room' ? 5 : 8
      arr[i * 3] = (Math.random() - 0.5) * spread
      arr[i * 3 + 1] = (Math.random() - 0.5) * 6 + 1
      arr[i * 3 + 2] = (Math.random() - 0.5) * spread
    }
    return arr
  }, [count, world])

  // Map colors
  const getParticleColor = () => {
    if (world === 'neon-room') return '#bf5af2'
    if (world === 'iron-lab') return '#ff9f0a'
    if (world === 'cyber-city') return '#ff375f'
    
    // Mood default fallback
    return mood === 'excited' ? '#ff375f' : '#00f0ff'
  }

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        color={getParticleColor()}
        size={world === 'space-station' ? 0.06 : 0.03}
        sizeAttenuation
        transparent
        opacity={0.7}
        depthWrite={false}
      />
    </points>
  )
}

// Glowing Core Reactor (AI Energy Core) in the center of the scene
function EnergyCore({ mood, micActive, world }) {
  const coreRef = useRef()
  const ringRef1 = useRef()
  const ringRef2 = useRef()

  const getMoodColor = () => {
    switch (mood) {
      case 'sad': return '#0a84ff'
      case 'excited': return '#ff375f'
      case 'tired': return '#ff9f0a'
      case 'happy':
      default:
        return '#00f0ff'
    }
  }

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    const color = getMoodColor()
    
    // Pulse animation based on speech/mic inputs
    if (coreRef.current) {
      const baseScale = world === 'iron-lab' ? 0.35 : 0.28
      const pulse = micActive 
        ? baseScale + Math.abs(Math.sin(t * 30)) * 0.15 
        : baseScale + Math.sin(t * 2) * 0.03
      
      coreRef.current.scale.set(pulse, pulse, pulse)
      coreRef.current.rotation.y = t * 0.5
    }

    // Spin outer ring layers
    if (ringRef1.current) {
      ringRef1.current.rotation.z = t * 1.5
      ringRef1.current.rotation.x = t * 0.4
    }
    if (ringRef2.current) {
      ringRef2.current.rotation.y = -t * 1.2
      ringRef2.current.rotation.z = t * 0.6
    }
  })

  const coreColor = getMoodColor()

  return (
    <group position={[0, -0.65, 0]}>
      {/* Central energy sphere */}
      <mesh ref={coreRef}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial 
          color={coreColor} 
          transparent 
          opacity={0.7} 
          wireframe={world === 'cyber-city'} 
        />
        <pointLight intensity={3} distance={5} color={coreColor} />
      </mesh>

      {/* Rotating technical containment rings */}
      <mesh ref={ringRef1} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.55, 0.02, 8, 32]} />
        <meshBasicMaterial color={coreColor} transparent opacity={0.5} />
      </mesh>
      
      <mesh ref={ringRef2} rotation={[0, Math.PI / 4, 0]}>
        <torusGeometry args={[0.65, 0.015, 8, 32]} />
        <meshBasicMaterial color={world === 'neon-room' ? '#bf5af2' : '#ffffff'} transparent opacity={0.3} />
      </mesh>
    </group>
  )
}

// AI clones that orbit the platform when activated
function AIClones({ cloneMode, mood }) {
  const clonesGroup = useRef()

  useFrame((state) => {
    if (clonesGroup.current && cloneMode) {
      clonesGroup.current.rotation.y = state.clock.getElapsedTime() * 0.6
    }
  })

  if (!cloneMode) return null

  const getMoodColor = () => {
    if (mood === 'excited') return '#ff375f'
    if (mood === 'sad') return '#0a84ff'
    return '#00f0ff'
  }

  // Orbiting clones positions
  return (
    <group ref={clonesGroup} position={[0, 0.3, 0]}>
      {/* Clone 1: Coding Jarvis */}
      <group position={[1.4, 0, 0]}>
        <mesh>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color={getMoodColor()} transparent opacity={0.8} wireframe />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.2, 0.005, 4, 16]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.3} />
        </mesh>
      </group>

      {/* Clone 2: Research Jarvis */}
      <group position={[-1.2, 0.3, 0.8]}>
        <mesh>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color="#bf5af2" transparent opacity={0.8} wireframe />
        </mesh>
        <mesh rotation={[0, Math.PI / 4, 0]}>
          <torusGeometry args={[0.2, 0.005, 4, 16]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.3} />
        </mesh>
      </group>

      {/* Clone 3: Study Jarvis */}
      <group position={[-0.8, -0.2, -1.2]}>
        <mesh>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color="#ff9f0a" transparent opacity={0.8} wireframe />
        </mesh>
      </group>
    </group>
  )
}

// Environmental Grids and Platform
function FloorGrid({ world, mood }) {
  const getGridColor = () => {
    if (world === 'neon-room') return '#bf5af2'
    if (world === 'iron-lab') return '#ff9f0a'
    if (world === 'future-office') return '#444444'
    if (world === 'cyber-city') return '#ff375f'
    
    // Mood color default fallback
    return mood === 'excited' ? '#ff375f' : '#00f0ff'
  }

  const gridColor = getGridColor()

  return (
    <group position={[0, -2, 0]}>
      {/* Radial grid floor */}
      <gridHelper args={[30, 30, gridColor, '#121218']} opacity={0.2} transparent />
      
      {/* Holographic projection base platform */}
      <mesh position={[0, 0.01, 0]}>
        <cylinderGeometry args={[1.5, 1.7, 0.08, 32]} />
        <meshStandardMaterial 
          color={gridColor} 
          wireframe 
          transparent 
          opacity={0.2} 
        />
      </mesh>
    </group>
  )
}

export default function HologramCanvas({ hologramMode, mood, micActive, avatarUrl, world, cloneMode }) {
  // Map world settings to lighting configs
  const getAmbientIntensity = () => {
    if (world === 'future-office') return 0.7
    if (world === 'space-station') return 0.25
    return 0.4
  }

  const getSpotlightColor = () => {
    if (hologramMode) return '#00f0ff'
    if (world === 'neon-room') return '#bf5af2'
    if (world === 'iron-lab') return '#ff9f0a'
    
    switch (mood) {
      case 'excited': return '#ff375f'
      case 'sad': return '#0a84ff'
      case 'tired': return '#ff9f0a'
      default: return '#00f0ff'
    }
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'absolute', top: 0, left: 0, zIndex: 1 }}>
      <Canvas style={{ background: '#020208' }}>
        <PerspectiveCamera makeDefault position={[0, 0.5, 4.5]} fov={55} />
        
        {/* Dynamic World Ambient Lighting */}
        <ambientLight intensity={getAmbientIntensity()} />
        <pointLight position={[5, 8, 5]} intensity={1.2} color={getSpotlightColor()} />
        <pointLight position={[-5, 5, -5]} intensity={0.6} color={world === 'neon-room' ? '#bf5af2' : '#00f0ff'} />
        
        {/* Holographic Platform Projection Spotlight */}
        <spotLight 
          position={[0, -2, 0]} 
          angle={0.7} 
          penumbra={1} 
          intensity={4} 
          color={getSpotlightColor()} 
        />

        {/* 3D Animated Avatar */}
        <Avatar 
          hologramMode={hologramMode} 
          mood={mood} 
          micActive={micActive} 
          avatarUrl={avatarUrl}
        />

        {/* AI Energy Core */}
        <EnergyCore mood={mood} micActive={micActive} world={world} />

        {/* AI Clones */}
        <AIClones cloneMode={cloneMode} mood={mood} />

        {/* Environments Grid and VFX */}
        <FloorGrid world={world} mood={mood} />
        <CustomEnvironmentParticles count={world === 'space-station' ? 400 : 200} world={world} mood={mood} />
        <Stars radius={120} depth={50} count={world === 'space-station' ? 800 : 250} factor={world === 'space-station' ? 6 : 3} saturation={0.6} fade speed={1.2} />

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
