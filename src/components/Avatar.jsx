import React, { useRef, useState, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

// Procedural 3D Robot Avatar matching the user's reference image
function ProceduralAvatar({ hologramMode, mood, micActive }) {
  const groupRef = useRef()
  const headRef = useRef()
  const leftEyeGroup = useRef()
  const rightEyeGroup = useRef()
  const mouthRef = useRef()
  const logoRef = useRef()
  
  // Left/Right Braid/Horns (Robot Tech-Wings)
  const leftHornRef = useRef()
  const rightHornRef = useRef()

  // Blink timing variables
  const blinkTimer = useRef(0)
  const isBlinking = useRef(false)

  // Map colors based on mood and hologram filters
  const getColors = () => {
    if (hologramMode) {
      return { 
        shell: '#00f0ff', 
        visor: '#002b33', 
        glow: '#00f0ff', 
        details: '#00ccff',
        wireframe: true 
      }
    }
    
    switch (mood) {
      case 'sad':
        return { shell: '#e2e8f0', visor: '#051122', glow: '#0a84ff', details: '#0055aa', wireframe: false }
      case 'excited':
        return { shell: '#e2e8f0', visor: '#220511', glow: '#ff375f', details: '#cc0044', wireframe: false }
      case 'tired':
        return { shell: '#b0b8c4', visor: '#1a1005', glow: '#ff9f0a', details: '#cc7700', wireframe: false }
      case 'happy':
      default:
        return { shell: '#ffffff', visor: '#0a0d1a', glow: '#00f0ff', details: '#0088aa', wireframe: false }
    }
  }

  const colors = getColors()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    const speedMultiplier = mood === 'excited' ? 2 : mood === 'tired' ? 0.5 : 1

    // 1. Idle Breathing Animation (bobbing group)
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(t * 1.6 * speedMultiplier) * 0.06 + 0.35
      groupRef.current.rotation.y = Math.sin(t * 0.15) * 0.05
    }

    // 2. Head subtle tilt
    if (headRef.current) {
      headRef.current.rotation.x = Math.sin(t * 0.7) * 0.03
      headRef.current.rotation.z = Math.cos(t * 0.4) * 0.015
    }

    // 3. Eye Blinking Logic (scales eyes group Y axis)
    blinkTimer.current += state.delta
    if (blinkTimer.current > 3.5 + Math.random() * 3 && !isBlinking.current) {
      isBlinking.current = true
      blinkTimer.current = 0
    }

    if (isBlinking.current) {
      const scale = leftEyeGroup.current.scale.y
      if (scale > 0.05) {
        leftEyeGroup.current.scale.y = Math.max(0.01, scale - state.delta * 22)
        rightEyeGroup.current.scale.y = Math.max(0.01, scale - state.delta * 22)
      } else {
        isBlinking.current = false
      }
    } else {
      const scale = leftEyeGroup.current.scale.y
      if (scale < 1) {
        leftEyeGroup.current.scale.y = Math.min(1, scale + state.delta * 16)
        rightEyeGroup.current.scale.y = Math.min(1, scale + state.delta * 16)
      }
    }

    // 4. Forehead science/atom symbol spinning
    if (logoRef.current) {
      logoRef.current.rotation.y = t * 1.5
    }

    // 5. Lip-sync animation (mouth mesh scales Y and X slightly based on mic volume/sines)
    if (mouthRef.current) {
      if (micActive) {
        const mouthScale = 0.3 + Math.abs(Math.sin(t * 22)) * 1.2
        mouthRef.current.scale.y = mouthScale
        mouthRef.current.scale.x = 0.9 + Math.abs(Math.cos(t * 15)) * 0.3
      } else {
        mouthRef.current.scale.y = THREE.MathUtils.lerp(mouthRef.current.scale.y, 0.15, 0.1)
        mouthRef.current.scale.x = THREE.MathUtils.lerp(mouthRef.current.scale.x, 1, 0.1)
      }
    }

    // 6. Top Tech-Wings (Horns) subtle swaying
    if (leftHornRef.current && rightHornRef.current) {
      leftHornRef.current.rotation.z = Math.sin(t * 1.2) * 0.03 + 0.1
      rightHornRef.current.rotation.z = -Math.sin(t * 1.2) * 0.03 - 0.1
    }
  })

  return (
    <group ref={groupRef} position={[0, 0.35, 0]}>
      
      {/* 3D Robot Head (White glossy helmet shell) */}
      <mesh ref={headRef}>
        <sphereGeometry args={[0.62, 32, 32]} />
        <meshStandardMaterial
          color={colors.shell}
          wireframe={colors.wireframe}
          roughness={0.15}
          metalness={0.2}
        />

        {/* Visor Screen (Dark blue visor panel) */}
        <mesh position={[0, -0.05, 0.22]} scale={[1.05, 0.5, 0.7]}>
          <sphereGeometry args={[0.62, 16, 16, 0, Math.PI * 2, 0.7, 1.8]} />
          <meshStandardMaterial
            color={colors.visor}
            roughness={0.05}
            metalness={0.9}
          />
        </mesh>

        {/* EYES: Concentric glowing blue circular rings */}
        <group position={[0, -0.05, 0.55]}>
          {/* Left Eye */}
          <group ref={leftEyeGroup} position={[-0.22, 0, 0]}>
            {/* Outer Ring */}
            <mesh>
              <torusGeometry args={[0.11, 0.015, 8, 32]} />
              <meshBasicMaterial color={colors.glow} />
            </mesh>
            {/* Inner pupil */}
            <mesh scale={[0.8, 0.8, 0.8]}>
              <sphereGeometry args={[0.04, 16, 16]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>

          {/* Right Eye */}
          <group ref={rightEyeGroup} position={[0.22, 0, 0]}>
            {/* Outer Ring */}
            <mesh>
              <torusGeometry args={[0.11, 0.015, 8, 32]} />
              <meshBasicMaterial color={colors.glow} />
            </mesh>
            {/* Inner pupil */}
            <mesh scale={[0.8, 0.8, 0.8]}>
              <sphereGeometry args={[0.04, 16, 16]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>
        </group>

        {/* Forehead Atom Symbol (Logo from the image) */}
        <group ref={logoRef} position={[0, 0.32, 0.44]} scale={[0.12, 0.12, 0.12]}>
          {/* Central dot */}
          <mesh>
            <sphereGeometry args={[0.25, 16, 16]} />
            <meshBasicMaterial color={colors.glow} />
          </mesh>
          {/* Ring 1 */}
          <mesh rotation={[Math.PI / 4, 0, 0]}>
            <torusGeometry args={[0.7, 0.06, 6, 24]} />
            <meshBasicMaterial color="#000000" />
          </mesh>
          {/* Ring 2 */}
          <mesh rotation={[-Math.PI / 4, Math.PI / 3, 0]}>
            <torusGeometry args={[0.7, 0.06, 6, 24]} />
            <meshBasicMaterial color="#000000" />
          </mesh>
          {/* Ring 3 */}
          <mesh rotation={[0, -Math.PI / 3, Math.PI / 4]}>
            <torusGeometry args={[0.7, 0.06, 6, 24]} />
            <meshBasicMaterial color="#000000" />
          </mesh>
        </group>

        {/* Side Headphones (Ear caps) */}
        {/* Left Ear */}
        <group position={[-0.64, -0.05, 0]} rotation={[0, 0, Math.PI / 2]}>
          <mesh>
            <cylinderGeometry args={[0.15, 0.18, 0.12, 16]} />
            <meshStandardMaterial color={colors.shell} roughness={0.15} metalness={0.2} />
          </mesh>
          <mesh position={[0, 0.07, 0]}>
            <cylinderGeometry args={[0.1, 0.1, 0.02, 16]} />
            <meshBasicMaterial color={colors.glow} />
          </mesh>
        </group>
        {/* Right Ear */}
        <group position={[0.64, -0.05, 0]} rotation={[0, 0, -Math.PI / 2]}>
          <mesh>
            <cylinderGeometry args={[0.15, 0.18, 0.12, 16]} />
            <meshStandardMaterial color={colors.shell} roughness={0.15} metalness={0.2} />
          </mesh>
          <mesh position={[0, 0.07, 0]}>
            <cylinderGeometry args={[0.1, 0.1, 0.02, 16]} />
            <meshBasicMaterial color={colors.glow} />
          </mesh>
        </group>

        {/* Tech Wings / Curved Antennas (Horns on top) */}
        {/* Left Horn */}
        <mesh ref={leftHornRef} position={[-0.34, 0.54, 0]} rotation={[0, 0.2, 0.1]}>
          <torusGeometry args={[0.22, 0.04, 8, 32, Math.PI * 0.7]} />
          <meshStandardMaterial color={colors.shell} roughness={0.15} />
        </mesh>
        {/* Right Horn */}
        <mesh ref={rightHornRef} position={[0.34, 0.54, 0]} rotation={[0, -0.2, -0.1]}>
          <torusGeometry args={[0.22, 0.04, 8, 32, Math.PI * 0.7]} />
          <meshStandardMaterial color={colors.shell} roughness={0.15} />
        </mesh>

        {/* Robot Smile (Mouth indicator) */}
        <mesh ref={mouthRef} position={[0, -0.26, 0.46]} rotation={[0, 0, 0]}>
          <boxGeometry args={[0.1, 0.015, 0.02]} />
          <meshBasicMaterial color={colors.glow} />
        </mesh>
      </mesh>

      {/* Cyber Neck (Metallic grooved connector) */}
      <mesh position={[0, -0.72, 0]}>
        <cylinderGeometry args={[0.13, 0.15, 0.26, 16]} />
        <meshStandardMaterial color="#1f2937" roughness={0.4} metalness={0.8} />
      </mesh>

      {/* Chest Armor Plate */}
      <mesh position={[0, -1.0, 0]}>
        <cylinderGeometry args={[0.38, 0.62, 0.35, 32]} />
        <meshStandardMaterial color={colors.shell} roughness={0.2} metalness={0.15} />
      </mesh>

      {/* Chest Glowing Triangle Light (Chest core) */}
      <group position={[0, -0.92, 0.44]} rotation={[0, 0, Math.PI]}>
        <mesh>
          <coneGeometry args={[0.08, 0.12, 3]} />
          <meshBasicMaterial color={colors.glow} />
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
      
      const head = scene.getObjectByName('Head') || scene.getObjectByName('Neck')
      if (head) {
        head.rotation.y = Math.sin(t * 0.25) * 0.08
        head.rotation.x = Math.sin(t * 0.6) * 0.04
      }

      const mouth = scene.getObjectByName('Mouth') || scene.getObjectByName('Beard')
      if (mouth && micActive) {
        mouth.scale.y = 1 + Math.abs(Math.sin(t * 22)) * 0.25
      }
    }
  })

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
