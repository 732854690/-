import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
import math
import time
import matplotlib.colors as mcolors
from collections import deque
from matplotlib.collections import LineCollection


# Class to represent a point (used as base class for Video and User)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Class to represent a Video
class Video(Point):
    def __init__(self, x, y, type, quality, tags, duration, excitement, visit_count, like_count, comment_count,
                 share_count, creation_time):
        super().__init__(x, y)
        self.type = type
        self.quality = quality
        self.tags = tags
        self.duration = duration
        self.excitement = excitement
        self.visit_count = visit_count
        self.like_count = like_count
        self.comment_count = comment_count
        self.share_count = share_count
        self.creation_time = creation_time
        self.color = self.get_color()

    def get_color(self):
        # Return color based on the video type
        colors = {
            'Technology': 'blue',
            'Entertainment': 'purple',
            'Food': 'orange',
            'Vlog': 'green'
        }
        return colors[self.type]


# Class to represent a User
class User(Point):
    def __init__(self, x, y, preferences, engagement_rate, preferred_duration):
        super().__init__(x, y)
        self.starting_point = (x, y)
        self.segments = []
        self.target = None
        self.visited = deque(maxlen=15)  # Track last 15 visited videos
        self.preferences = preferences
        self.engagement_rate = engagement_rate
        self.preferred_duration = preferred_duration

    def move_towards(self, target):
        # Move user towards the target video
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist > 0:
            step_size = 0.1  # Adjust step size for smoother movement
            self.x += dx / dist * step_size
            self.y += dy / dist * step_size
            if dist < step_size:
                self.segments.append(((self.starting_point, (self.x, self.y)), target.color))  # Store segment and color
                self.starting_point = (self.x, self.y)  # Update starting point
                return True
        return False


def calculate_probability(video, user):
    # Calculate the probability of a user interacting with a video
    current_time = time.time()
    age_factor = 1 / (1 + current_time - video.creation_time)
    engagement_factor = (video.like_count + video.comment_count + video.share_count) / max(1, video.visit_count)
    quality_factor = video.quality
    duration_factor = 1 if video.duration == user.preferred_duration else 0.5
    preference_factor = user.preferences[video.type]
    weight = (video.excitement + engagement_factor + quality_factor) * age_factor * preference_factor * duration_factor
    return weight


def update_users(users, videos):
    # Update user positions and interactions with videos
    for user in users:
        if user.target is None or user.move_towards(user.target):
            if user.target is not None:
                user.visited.append(user.target)
                user.target.visit_count += 1
                liked = False
                if random.random() < user.target.excitement * user.engagement_rate:
                    user.target.like_count += 1
                    user.target.comment_count += random.randint(0, 2)  # Random comments
                    user.target.share_count += random.randint(0, 1)  # Random shares
                    liked = True
                user.target.excitement += 0.1
                if not liked:
                    user.segments[-1] = (user.segments[-1][0], 'white')  # Change to white if not liked
        possible_targets = [video for video in videos if video not in user.visited]
        if possible_targets:
            user.target = max(possible_targets, key=lambda v: calculate_probability(v, user))
        else:
            user.target = min(videos, key=lambda v: calculate_probability(v, user))  # Allow revisits after all visited


def generate_videos(num_videos, margin=1.0):
    # Generate a list of video objects
    def is_far_enough(x, y, points, min_dist=1.0):
        for px, py in points:
            if math.sqrt((x - px) ** 2 + (y - py) ** 2) < min_dist:
                return False
        return True

    types = ['Technology', 'Entertainment', 'Food', 'Vlog']
    videos = []
    points = []
    for t in types:
        cluster_center = (random.uniform(margin, 10 - margin), random.uniform(margin, 10 - margin))
        for _ in range(num_videos // 4):
            attempt_count = 0  # Debugging: Track attempts to generate a valid point
            while True:
                x = cluster_center[0] + random.uniform(-1, 1)
                y = cluster_center[1] + random.uniform(-1, 1)
                if is_far_enough(x, y, points) and margin < x < 10 - margin and margin < y < 10 - margin:
                    break
                attempt_count += 1
                if attempt_count > 1000:  # Debugging: Prevent infinite loop
                    print("Warning: Could not find a valid point within 1000 attempts")
                    break
            points.append((x, y))
            quality = random.uniform(0, 1)
            tags = [random.choice(['funny', 'tutorial', 'review', 'vlog', 'recipe']) for _ in range(3)]
            duration = random.choice(['short', 'medium', 'long'])
            videos.append(Video(x, y, t, quality, tags, duration, random.uniform(0, 1), 0, 0, 0, 0, time.time()))
    return videos


def generate_users(num_users, margin=1.0):
    # Generate a list of user objects
    users = []
    for _ in range(num_users):
        attempt_count = 0  # Debugging: Track attempts to generate a valid point
        while True:
            x = random.uniform(margin, 10 - margin)
            y = random.uniform(margin, 10 - margin)
            preferences = {
                'Technology': random.uniform(0, 1),
                'Entertainment': random.uniform(0, 1),
                'Food': random.uniform(0, 1),
                'Vlog': random.uniform(0, 1)
            }
            total = sum(preferences.values())
            for k in preferences:
                preferences[k] /= total
            engagement_rate = random.uniform(0.5, 1.5)
            preferred_duration = random.choice(['short', 'medium', 'long'])
            if margin < x < 10 - margin and margin < y < 10 - margin:
                users.append(User(x, y, preferences, engagement_rate, preferred_duration))
                break
            attempt_count += 1
            if attempt_count > 1000:  # Debugging: Prevent infinite loop
                print("Warning: Could not find a valid point within 1000 attempts")
                break
    return users


def periodic_updates(users, videos, max_users=100, max_videos=30, margin=1.0):
    # Periodically update the list of users and videos
    new_videos = generate_videos(random.randint(1, 5), margin)
    videos.extend(new_videos)
    if len(videos) > max_videos:
        videos = videos[-max_videos:]

    if users:
        num_remove = random.randint(0, len(users))  # Remove 0 to 100% of users
        users = users[num_remove:]

    new_users = generate_users(random.randint(1, 5), margin)
    users.extend(new_users)
    if len(users) > max_users:
        users = users[-max_users:]

    return users, videos


def animate(i, users, videos, scat_users, scat_videos, line_collections, text_annotations, ax):
    # Animation function to update the plot
    if i % 200 == 0:  # Adjust interval for periodic updates
        users, videos = periodic_updates(users, videos)

    update_users(users, videos)
    scat_users.set_offsets([(user.x, user.y) for user in users])
    scat_videos.set_offsets([(video.x, video.y) for video in videos])
    scat_videos.set_color([video.color for video in videos])

    for line_collection, user in zip(line_collections, users):
        segments = [segment for segment, color in user.segments]
        colors = [mcolors.to_rgba(color, alpha=0.05) if color != 'white' else mcolors.to_rgba(color, alpha=0.05) for
                  segment, color in user.segments]
        line_collection.set_segments(segments)
        line_collection.set_color(colors)
        line_collection.set_zorder(1)  # Ensure lines are below points and text

    # Clear existing text annotations
    while text_annotations:
        text_annotations.pop().remove()

    # Redraw video information
    for video in videos:
        annotation = ax.text(video.x, video.y + 0.2,
                             f"E: {video.excitement:.2f}\nL: {video.like_count}\nC: {video.comment_count}\nS: {video.share_count}",
                             color='white', fontsize=8, ha='center', zorder=5)
        text_annotations.append(annotation)

    scat_users.set_zorder(4)  # Ensure users are on top
    scat_videos.set_zorder(4)  # Ensure videos are on top

    return scat_users, scat_videos, *line_collections, *text_annotations


def main():
    margin = 1.0  # Adjust the margin width here
    num_users = 50  # Initial number of users
    num_videos = 20  # Initial number of videos

    users = generate_users(num_users, margin)
    videos = generate_videos(num_videos, margin)

    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_facecolor('black')  # Set background color to black

    scat_users = ax.scatter([user.x for user in users], [user.y for user in users], c='white', s=10,
                            zorder=4)  # Smaller size for users
    scat_videos = ax.scatter([video.x for video in videos], [video.y for video in videos],
                             c=[video.color for video in videos], s=50, zorder=4)  # Larger size for videos
    line_collections = [LineCollection([], lw=2, zorder=1) for _ in users]
    for line_collection in line_collections:
        ax.add_collection(line_collection)

    # Add a legend for the video types
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Technology', markersize=10, markerfacecolor='blue'),
        plt.Line2D([0], [0], marker='o', color='w', label='Entertainment', markersize=10, markerfacecolor='purple'),
        plt.Line2D([0], [0], marker='o', color='w', label='Food', markersize=10, markerfacecolor='orange'),
        plt.Line2D([0], [0], marker='o', color='w', label='Vlog', markersize=10, markerfacecolor='green')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    text_annotations = []

    # Animation function call with ax passed as an argument
    ani = animation.FuncAnimation(
        fig, animate, frames=10000,
        fargs=(users, videos, scat_users, scat_videos, line_collections, text_annotations, ax), interval=50, blit=True
    )

    plt.show()


if __name__ == "__main__":
    main()
