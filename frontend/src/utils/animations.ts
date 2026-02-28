/**
 * GSAP animation utilities
 */

import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger)

/**
 * Animate number counter
 */
export const animateCounter = (
    element: HTMLElement,
    targetValue: number,
    duration: number = 2,
    onUpdate?: (value: number) => void
): gsap.core.Tween => {
    return gsap.to(element, {
        textContent: targetValue,
        duration,
        snap: { textContent: 1 },
        ease: 'power2.out',
        onUpdate() {
            if (onUpdate) {
                onUpdate(parseInt(element.textContent || '0'))
            }
        },
    })
}

/**
 * Staggered list animation
 */
export const animateListItems = (
    selector: string,
    duration: number = 0.6,
    stagger: number = 0.1
): gsap.core.Tween => {
    return gsap.to(selector, {
        opacity: 1,
        y: 0,
        duration,
        stagger,
        ease: 'back.out',
    })
}

/**
 * Fade in animation
 */
export const fadeIn = (
    element: HTMLElement | string,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        opacity: 1,
        duration,
        delay,
        ease: 'power2.out',
    })
}

/**
 * Fade out animation
 */
export const fadeOut = (
    element: HTMLElement | string,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        opacity: 0,
        duration,
        delay,
        ease: 'power2.in',
    })
}

/**
 * Scale animation
 */
export const scale = (
    element: HTMLElement | string,
    targetScale: number = 1,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        scale: targetScale,
        duration,
        delay,
        ease: 'back.out',
    })
}

/**
 * Slide in from left
 */
export const slideInLeft = (
    element: HTMLElement | string,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        x: 0,
        opacity: 1,
        duration,
        delay,
        ease: 'power2.out',
    })
}

/**
 * Slide in from right
 */
export const slideInRight = (
    element: HTMLElement | string,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        x: 0,
        opacity: 1,
        duration,
        delay,
        ease: 'power2.out',
    })
}

/**
 * Slide in from top
 */
export const slideInTop = (
    element: HTMLElement | string,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        y: 0,
        opacity: 1,
        duration,
        delay,
        ease: 'power2.out',
    })
}

/**
 * Slide in from bottom
 */
export const slideInBottom = (
    element: HTMLElement | string,
    duration: number = 0.5,
    delay: number = 0
): gsap.core.Tween => {
    return gsap.to(element, {
        y: 0,
        opacity: 1,
        duration,
        delay,
        ease: 'power2.out',
    })
}

/**
 * Bounce animation
 */
export const bounce = (
    element: HTMLElement | string,
    duration: number = 0.6
): gsap.core.Tween => {
    return gsap.to(element, {
        y: -10,
        duration: duration / 2,
        ease: 'power2.out',
        yoyo: true,
        repeat: 1,
    })
}

/**
 * Pulse animation
 */
export const pulse = (
    element: HTMLElement | string,
    duration: number = 1
): gsap.core.Tween => {
    return gsap.to(element, {
        scale: 1.1,
        duration: duration / 2,
        ease: 'power2.inOut',
        yoyo: true,
        repeat: -1,
    })
}

/**
 * Rotate animation
 */
export const rotate = (
    element: HTMLElement | string,
    degrees: number = 360,
    duration: number = 1
): gsap.core.Tween => {
    return gsap.to(element, {
        rotation: degrees,
        duration,
        ease: 'power2.inOut',
    })
}

/**
 * Hover scale effect
 */
export const setupHoverScale = (
    element: HTMLElement,
    scale: number = 1.05,
    duration: number = 0.3
): void => {
    element.addEventListener('mouseenter', () => {
        gsap.to(element, {
            scale,
            duration,
            ease: 'power2.out',
        })
    })

    element.addEventListener('mouseleave', () => {
        gsap.to(element, {
            scale: 1,
            duration,
            ease: 'power2.out',
        })
    })
}

/**
 * Scroll trigger animation
 */
export const setupScrollTrigger = (
    selector: string,
    options: {
        trigger?: string
        start?: string
        end?: string
        scrub?: boolean | number
        markers?: boolean
    } = {}
): gsap.core.Tween => {
    return gsap.to(selector, {
        scrollTrigger: {
            trigger: options.trigger || selector,
            start: options.start || 'top 80%',
            end: options.end || 'top 20%',
            scrub: options.scrub || false,
            markers: options.markers || false,
        },
        opacity: 1,
        y: 0,
        duration: 1,
    })
}

/**
 * Timeline animation
 */
export const createTimeline = (): gsap.core.Timeline => {
    return gsap.timeline()
}

/**
 * Kill all animations
 */
export const killAll = (): void => {
    gsap.killTweensOf('*')
}

/**
 * Kill animations for specific element
 */
export const kill = (element: HTMLElement | string): void => {
    gsap.killTweensOf(element)
}

/**
 * Pause all animations
 */
export const pauseAll = (): void => {
    gsap.globalTimeline.pause()
}

/**
 * Resume all animations
 */
export const resumeAll = (): void => {
    gsap.globalTimeline.resume()
}

export default {
    animateCounter,
    animateListItems,
    fadeIn,
    fadeOut,
    scale,
    slideInLeft,
    slideInRight,
    slideInTop,
    slideInBottom,
    bounce,
    pulse,
    rotate,
    setupHoverScale,
    setupScrollTrigger,
    createTimeline,
    killAll,
    kill,
    pauseAll,
    resumeAll,
}
