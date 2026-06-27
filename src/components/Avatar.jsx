import React, { useRef, useState, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

// Procedural Hologram Bust representing the female AI Jarvis assistant
function ProceduralAvatar({ hologramMode, mood, micActive }) {
  const groupRef = useRef()
  const headRef = useRef()
  const leftEyeRef = useRef()
  const rightEyeRef = useRef()
  const mouthRef = useRef()
  const orbitRef1 = useRef()
  const orbitRef2 = useRef()
  
  // Left/Right Braids (Procedural Hair detail for female avatar look)
  const leftBraidRef = useRef()
  const rightBraidRef = useRef()

  // Blink timing variables
  const blinkTimer = useRef(0)
  const isBlinking = useRef(false)

  // Mood color maps
  const getColors = () => {
    if (hologramMode) return { primary: '#00f0ff', secondary: '#005577', eyeColor: '#00f0ff', hairColor: '#00ccff' }
    
    switch (mood) {
      case 'sad':
        return { primary: '#0a84ff', secondary: '#002b55', eyeColor: '#00a3ff', hairColor: '#0055aa' }
      case 'excited':
        return { primary: '#ff375f', secondary: '#550011', eyeColor: '#ff0033', hairColor: '#cc0044' }
      case 'tired':
        return { primary: '#ff9f0a', secondary: '#553300', eyeColor: '#ffbb00', hairColor: '#cc7700' }
      case 'happy':
      default:
        return { primary: '#00f0ff', secondary: '#002b33', eyeColor: '#5ff0ff', hairColor: '#0088aa' }
    }
  }

  const colors = getColors()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    const speedMultiplier = mood === 'excited' ? 2 : mood === 'tired' ? 0.5 : 1

    // 1. Idle Breathing Animation (bobbing group)
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(t * 1.5 * speedMultiplier) * 0.08 + 0.35
      groupRef.current.rotation.y = Math.sin(t * 0.15) * 0.08
    }

    // 2. Head Tilt & Rotation
    if (headRef.current) {
      headRef.current.rotation.x = Math.sin(t * 0.8) * 0.04
      headRef.current.rotation.z = Math.cos(t * 0.4) * 0.02
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

    // 4. Lip-sync animation (scale mouth mesh based on mic levels)
    if (mouthRef.current) {
      if (micActive) {
        const mouthScale = 0.2 + Math.abs(Math.sin(t * 22)) * 1.4
        mouthRef.current.scale.y = mouthScale
        mouthRef.current.scale.x = 0.8 + Math.abs(Math.cos(t * 12)) * 0.3
      } else {
        mouthRef.current.scale.y = THREE.MathUtils.lerp(mouthRef.current.scale.y, 0.15, 0.1)
        mouthRef.current.scale.x = THREE.MathUtils.lerp(mouthRef.current.scale.x, 1, 0.1)
      }
    }

    // 5. Hair braid animations (swaying)
    if (leftBraidRef.current && rightBraidRef.current) {
      leftBraidRef.current.rotation.z = Math.sin(t * 1.5) * 0.06 - 0.15
      rightBraidRef.current.rotation.z = -Math.sin(t * 1.5) * 0.06 + 0.15
    }

    // 6. Gyroscopic Orbit Halos Rotation
    if (orbitRef1.current) {
      orbitRef1.current.rotation.z = t * 0.7 * speedMultiplier
      orbitRef1.current.rotation.x = t * 0.3
    }
    if (orbitRef2.current) {
      orbitRef2.current.rotation.y = -t * 0.5 * speedMultiplier
      orbitRef2.current.rotation.z = t * 0.25
    }
  })

  return (
    <group ref={groupRef} position={[0, 0.35, 0]}>
      {/* 3D Hologram Head Body */}
      <mesh ref={headRef}>
        <sphereGeometry args={[0.55, 32, 32]} />
        <meshStandardMaterial
          color={colors.primary}
          wireframe={true}
          transparent={true}
          opacity={0.3}
          roughness={0.15}
          metalness={0.8}
        />
        
        {/* Inner Glowing Core */}
        <mesh scale={[0.82, 0.82, 0.82]}>
          <sphereGeometry args={[0.55, 16, 16]} />
          <meshBasicMaterial
            color={colors.secondary}
            transparent={true}
            opacity={0.2}
          />
        </mesh>

        {/* EYES: Glowing female LED Visors */}
        <group position={[0, 0.12, 0.44]}>
          {/* Left Eye */}
          <mesh ref={leftEyeRef} position={[-0.2, 0, 0]}>
            <boxGeometry args={[0.13, 0.03, 0.05]} />
            <meshBasicMaterial color={colors.eyeColor} />
          </mesh>
          {/* Right Eye */}
          <mesh ref={rightEyeRef} position={[0.2, 0, 0]}>
            <boxGeometry args={[0.13, 0.03, 0.05]} />
            <meshBasicMaterial color={colors.eyeColor} />
          </mesh>
        </group>

        {/* Mouth/Voice feedback mesh */}
        <mesh ref={mouthRef} position={[0, -0.22, 0.48]}>
          <boxGeometry args={[0.16, 0.02, 0.02]} />
          <meshBasicMaterial color={colors.primary} />
        </mesh>

        {/* Female Hair Braid Elements (Procedural Cyber-Cylinders) */}
        <group position={[0, 0.2, 0.1]}>
          {/* Left Braid */}
          <mesh ref={leftBraidRef} position={[-0.52, -0.5, 0]} rotation={[0, 0, -0.15]}>
            <cylinderGeometry args={[0.04, 0.02, 0.8, 8]} />
            <meshStandardMaterial color={colors.hairColor} wireframe transparent opacity={0.35} />
          </mesh>
          {/* Right Braid */}
          <mesh ref={rightBraidRef} position={[0.52, -0.5, 0]} rotation={[0, 0, 0.15]}>
            <cylinderGeometry args={[0.04, 0.02, 0.8, 8]} />
            <meshStandardMaterial color={colors.hairColor} wireframe transparent opacity={0.35} />
          </mesh>
        </group>
      </mesh>

      {/* Cyber Neck Column */}
      <mesh position={[0, -0.7, 0]}>
        <cylinderGeometry args={[0.14, 0.18, 0.35, 16]} />
        <meshStandardMaterial
          color={colors.primary}
          wireframe={true}
          transparent={true}
          opacity={0.2}
        />
      </mesh>

      {/* Collar / Shoulder Base */}
      <mesh position={[0, -0.95, 0]}>
        <cylinderGeometry args={[0.5, 0.8, 0.25, 32]} />
        <meshStandardMaterial
          color={colors.primary}
          wireframe={true}
          transparent={true}
          opacity={0.15}
        />
      </mesh>

      {/* Outer Gyroscopic Rings */}
      <group ref={orbitRef1} scale={[1.1, 1.1, 1.1]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.82, 0.012, 8, 64]} />
          <meshBasicMaterial color={colors.primary} transparent opacity={0.35} />
        </mesh>
      </group>

      <group ref={orbitRef2} scale={[1.18, 1.18, 1.18]} rotation={[Math.PI / 4, 0, 0]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.88, 0.008, 8, 48]} />
          <meshBasicMaterial color={colors.eyeColor} transparent opacity={0.2} />
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
    if (avatarRef.current) {
      avatarRef.current.position.y = Math.sin(t * 1.5) * 0.04 - 0.95
      
      // Simple head follow camera rotation
      const head = scene.getObjectByName('Head') || scene.getObjectByName('Neck')
      if (head) {
        head.rotation.y = Math.sin(t * 0.25) * 0.08
        head.rotation.x = Math.sin(t * 0.6) * 0.04
      }

      // Simple mouth lip sync scaling if mic is active
      const mouth = scene.getObjectByName('Mouth') || scene.getObjectByName('Beard')
      if (mouth && micActive) {
        mouth.scale.y = 1 + Math.abs(Math.sin(t * 22)) * 0.25
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
          child.material.opacity = 0.8
          if (child.material.color) {
            const tint = mood === 'excited' ? new THREE.Color('#ff375f') : new THREE.Color('#00f0ff')
            child.material.color.lerp(tint, 0.4)
          }
        }
      }
    })
  }, [scene, hologramMode, mood])

  return <primitive ref={avatarRef} object={scene} scale={[1.35, 1.35, 1.35]} position={[0, -0.95, 0]} />
}

export default function Avatar({ hologramMode, mood, micActive, avatarUrl }) {
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
