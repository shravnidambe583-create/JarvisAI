import React, { useRef, useState, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

// Procedural Hologram Bust fallback & main core design
function ProceduralAvatar({ hologramMode, mood, micActive }) {
  const groupRef = useRef()
  const headRef = useRef()
  const leftEyeRef = useRef()
  const rightEyeRef = useRef()
  const mouthRef = useRef()
  const orbitRef1 = useRef()
  const orbitRef2 = useRef()

  // Blink timing variables
  const blinkTimer = useRef(0)
  const isBlinking = useRef(false)

  // Mood color map
  const getColors = () => {
    if (hologramMode) return { primary: '#00f0ff', secondary: '#005577', eyeColor: '#00f0ff' }
    
    switch (mood) {
      case 'sad':
        return { primary: '#0a84ff', secondary: '#002b55', eyeColor: '#00a3ff' }
      case 'excited':
        return { primary: '#ff375f', secondary: '#550011', eyeColor: '#ff0033' }
      case 'tired':
        return { primary: '#ff9f0a', secondary: '#553300', eyeColor: '#ffbb00' }
      case 'happy':
      default:
        return { primary: '#00f0ff', secondary: '#002b33', eyeColor: '#5ff0ff' }
    }
  }

  const colors = getColors()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    const speedMultiplier = mood === 'excited' ? 2 : mood === 'tired' ? 0.5 : 1

    // 1. Idle Breathing Animation (bobbing group)
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(t * 1.5 * speedMultiplier) * 0.08
      groupRef.current.rotation.y = Math.sin(t * 0.2) * 0.1
    }

    // 2. Head Tilt & Rotation
    if (headRef.current) {
      headRef.current.rotation.x = Math.sin(t * 0.8) * 0.03
      headRef.current.rotation.z = Math.cos(t * 0.5) * 0.02
    }

    // 3. Eye Blinking Logic
    blinkTimer.current += state.delta
    if (blinkTimer.current > 3 + Math.random() * 3 && !isBlinking.current) {
      isBlinking.current = true
      blinkTimer.current = 0
    }

    if (isBlinking.current) {
      const scale = leftEyeRef.current.scale.y
      if (scale > 0.05) {
        leftEyeRef.current.scale.y = Math.max(0.01, scale - state.delta * 20)
        rightEyeRef.current.scale.y = Math.max(0.01, scale - state.delta * 20)
      } else {
        isBlinking.current = false
      }
    } else {
      const scale = leftEyeRef.current.scale.y
      if (scale < 1) {
        leftEyeRef.current.scale.y = Math.min(1, scale + state.delta * 15)
        rightEyeRef.current.scale.y = Math.min(1, scale + state.delta * 15)
      }
    }

    // 4. Lip-sync animation (scale mouth mesh based on mic levels/sine wave)
    if (mouthRef.current) {
      if (micActive) {
        const mouthScale = 0.2 + Math.abs(Math.sin(t * 22)) * 1.2
        mouthRef.current.scale.y = mouthScale
        mouthRef.current.scale.x = 0.8 + Math.abs(Math.cos(t * 10)) * 0.4
      } else {
        mouthRef.current.scale.y = THREE.MathUtils.lerp(mouthRef.current.scale.y, 0.1, 0.1)
        mouthRef.current.scale.x = THREE.MathUtils.lerp(mouthRef.current.scale.x, 1, 0.1)
      }
    }

    // 5. Gyroscopic Orbit Halos Rotation
    if (orbitRef1.current) {
      orbitRef1.current.rotation.z = t * 0.8 * speedMultiplier
      orbitRef1.current.rotation.x = t * 0.3
    }
    if (orbitRef2.current) {
      orbitRef2.current.rotation.y = -t * 0.6 * speedMultiplier
      orbitRef2.current.rotation.z = t * 0.2
    }
  })

  return (
    <group ref={groupRef} position={[0, 0.4, 0]}>
      {/* 3D Hologram Head Body */}
      <mesh ref={headRef}>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshStandardMaterial
          color={colors.primary}
          wireframe={true}
          transparent={true}
          opacity={0.3}
          roughness={0.1}
          metalness={0.9}
        />
        
        {/* Inner Glowing Core */}
        <mesh scale={[0.8, 0.8, 0.8]}>
          <sphereGeometry args={[0.5, 16, 16]} />
          <meshBasicMaterial
            color={colors.secondary}
            transparent={true}
            opacity={0.25}
          />
        </mesh>

        {/* Eyes (Glowing visors) */}
        <group position={[0, 0.15, 0.48]}>
          {/* Left Eye */}
          <mesh ref={leftEyeRef} position={[-0.22, 0, 0]}>
            <boxGeometry args={[0.15, 0.04, 0.05]} />
            <meshBasicMaterial color={colors.eyeColor} />
          </mesh>
          {/* Right Eye */}
          <mesh ref={rightEyeRef} position={[0.22, 0, 0]}>
            <boxGeometry args={[0.15, 0.04, 0.05]} />
            <meshBasicMaterial color={colors.eyeColor} />
          </mesh>
        </group>

        {/* Cyber-Mouth (Audio feedback line) */}
        <mesh ref={mouthRef} position={[0, -0.22, 0.52]}>
          <boxGeometry args={[0.2, 0.02, 0.02]} />
          <meshBasicMaterial color={colors.primary} />
        </mesh>
      </mesh>

      {/* Cyber Neck Connector */}
      <mesh position={[0, -0.75, 0]}>
        <cylinderGeometry args={[0.18, 0.22, 0.4, 16]} />
        <meshStandardMaterial
          color={colors.primary}
          wireframe={true}
          transparent={true}
          opacity={0.2}
        />
      </mesh>

      {/* Futuristic Collar/Shoulder Base */}
      <mesh position={[0, -1.05, 0]}>
        <cylinderGeometry args={[0.6, 0.9, 0.3, 32]} />
        <meshStandardMaterial
          color={colors.primary}
          wireframe={true}
          transparent={true}
          opacity={0.15}
        />
      </mesh>

      {/* Gyroscopic Tech Halos (Data Rings) */}
      <group ref={orbitRef1} scale={[1.1, 1.1, 1.1]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.85, 0.015, 8, 64]} />
          <meshBasicMaterial color={colors.primary} transparent opacity={0.4} />
        </mesh>
      </group>

      <group ref={orbitRef2} scale={[1.2, 1.2, 1.2]} rotation={[Math.PI / 4, 0, 0]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.9, 0.01, 8, 48]} />
          <meshBasicMaterial color={colors.eyeColor} transparent opacity={0.25} />
        </mesh>
      </group>
    </group>
  )
}

// Ready Player Me GLB Avatar Loader Wrapper (Loads model if provided, fallbacks procedurally if error/offline)
function GLBAvatar({ url, hologramMode, mood, micActive }) {
  const { scene } = useGLTF(url)
  const avatarRef = useRef()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    // Standard breathing loop for external GLB model
    if (avatarRef.current) {
      avatarRef.current.position.y = Math.sin(t * 1.5) * 0.04 - 1.0
      
      // Simple head follow camera rotation
      const head = scene.getObjectByName('Head') || scene.getObjectByName('Neck')
      if (head) {
        head.rotation.y = Math.sin(t * 0.3) * 0.08
        head.rotation.x = Math.sin(t * 0.7) * 0.04
      }

      // Simple mouth lip sync scaling if mic is active
      const mouth = scene.getObjectByName('Mouth') || scene.getObjectByName('Beard')
      if (mouth && micActive) {
        mouth.scale.y = 1 + Math.abs(Math.sin(t * 20)) * 0.2
      }
    }
  })

  // Modify materials dynamically to look holographic/glowing
  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh) {
        if (hologramMode) {
          child.material = new THREE.MeshBasicMaterial({
            color: '#00f0ff',
            wireframe: true,
            transparent: true,
            opacity: 0.4
          })
        } else {
          // Standard holographic gloss overlay
          child.material.transparent = true
          child.material.opacity = 0.85
          if (child.material.color) {
            // Apply slight tint based on mood
            const tint = mood === 'excited' ? new THREE.Color('#bf5af2') : new THREE.Color('#00f0ff')
            child.material.color.lerp(tint, 0.4)
          }
        }
      }
    })
  }, [scene, hologramMode, mood])

  return <primitive ref={avatarRef} object={scene} scale={[1.4, 1.4, 1.4]} position={[0, -1.0, 0]} />
}

export default function Avatar({ hologramMode, mood, micActive, avatarUrl }) {
  // If a valid avatarUrl is provided, try loading the RPM model, otherwise fallback to the procedure head
  if (avatarUrl) {
    try {
      return (
        <React.Suspense fallback={<ProceduralAvatar hologramMode={hologramMode} mood={mood} micActive={micActive} />}>
          <GLBAvatar url={avatarUrl} hologramMode={hologramMode} mood={mood} micActive={micActive} />
        </React.Suspense>
      )
    } catch (e) {
      console.warn("Ready Player Me GLB model failed to load. Falling back to main procedural mainframe avatar.", e)
      return <ProceduralAvatar hologramMode={hologramMode} mood={mood} micActive={micActive} />
    }
  }

  return <ProceduralAvatar hologramMode={hologramMode} mood={mood} micActive={micActive} />
}
