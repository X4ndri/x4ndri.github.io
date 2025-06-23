import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# Function to generate points on the curve lying on the oblique plane
def generate_curve_points(num_points=50):
    t = np.linspace(-1, 1, num_points)
    # Original coordinates
    x_orig = t
    y_orig = 0.5 * np.sin(3*t)
    
    # Rotation matrix for 45 degrees clockwise
    theta = -np.pi/4  # -45 degrees in radians
    rot_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                          [np.sin(theta), np.cos(theta)]])
    
    # Apply rotation to x and y coordinates
    x_rot, y_rot = np.dot(rot_matrix, np.vstack((x_orig, y_orig)))
    z = -0.5*x_rot - 0.5*y_rot
    return x_rot, y_rot, z

# Function to update the animation
def update(num, line, points):
    line.set_data(points[:2, :num])
    line.set_3d_properties(points[2, :num])

# Generate data points for the curve lying on the oblique plane
x, y, z = generate_curve_points()
points = np.vstack((x, y, z))

# Create the figure and axis
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Set the initial view angle
ax.view_init(elev=5, azim=5, roll=0)

# Set limits for the plot
ax.set_xlim(-1.5, 1)
ax.set_ylim(-1.5, 1)
ax.set_zlim(-1.5, 1)

ax.grid(False)
ax.axis('off')

# Draw the coordinate system with adjusted positions
ax.quiver(-1,-1,-1, 3, 0, 0, color='k', arrow_length_ratio=0.05, linewidth=2)
ax.quiver(-1,-1,-1, 0, 3, 0, color='k', arrow_length_ratio=0.05, linewidth=2)
ax.quiver(-1,-1,-1, 0, 0, 3, color='k', arrow_length_ratio=0.05, linewidth=2)

# Draw the oblique plane with adjusted orientation
xx, yy = np.meshgrid(np.linspace(-1, 1, 20), np.linspace(-1, 1, 20))
# Apply the same rotation to the plane grid
theta = 0.3*np.pi
rot_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
xx_rot, yy_rot = np.dot(rot_matrix, np.vstack((xx.flatten(), yy.flatten())))
xx_rot = xx_rot.reshape(xx.shape)
yy_rot = yy_rot.reshape(yy.shape)

zz = -0.7*xx_rot - 0.7*yy_rot
ax.plot_surface(xx_rot, yy_rot, zz, alpha=0.2, color='gray')

# Plot the initial points
ax.scatter(x[::4], y[::4], z[::4], c='black', alpha=0.8, s=9)

# Plot the initial curve
line, = ax.plot(x[:1], y[:1], z[:1], color='red', linewidth=2)

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=450, fargs=(line, points), interval=30)

# Show the animation
plt.show() 